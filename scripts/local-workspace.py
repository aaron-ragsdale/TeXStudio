from pathlib import Path
import json

def edit(path, old, new):
    p = Path(path)
    s = p.read_text()
    assert s.count(old) == 1, (path, old, s.count(old))
    p.write_text(s.replace(old, new, 1))

edit('src/types/auth.ts',
     '\tisGuest?: boolean;\n',
     '\tisGuest?: boolean;\n\tisLocalWorkspace?: boolean;\n')

p = Path('src/services/AuthService.ts')
s = p.read_text()
start = s.index('\t\t\t\t\t\tif (this.isGuestUser(user) && this.isGuestExpired(user)) {')
end = s.index('\n\t\t\t\t\t} else {', start)
s = s[:start] + """						// Preserve the existing project's owner ID when converting a legacy guest.
						if (this.isGuestUser(user)) {
							const localUser: User = {
								...user,
								username: 'Local Workspace',
								isGuest: false,
								isLocalWorkspace: true,
								sessionId: undefined,
								expiresAt: undefined,
							};
							await this.db.put(this.USER_STORE, localUser);
							this.currentUser = localUser;
						} else {
							this.currentUser = user;
						}""" + s[end:]
old = '\t\t\t// Run cleanup on initialization\n\t\t\tthis.cleanupExpiredGuests();'
assert old in s
s = s.replace(old, """			// Default to the persistent workspace; an explicit sign-out opens profile selection.
			if (!this.currentUser && localStorage.getItem('texstudio-profile-picker') !== 'true') {
				await this.openLocalWorkspace();
			}
			// Do not automatically delete legacy guest projects on startup.""", 1)
start = s.index('\tasync createGuestAccount(): Promise<User> {')
end = s.index('\n\tasync upgradeGuestAccount(', start)
s = s[:start] + """	// Kept for compatibility with the upstream authentication context.
	async createGuestAccount(): Promise<User> {
		if (!this.db) await this.initialize();
		return this.openLocalWorkspace();
	}

	private async openLocalWorkspace(): Promise<User> {
		const db = this.db;
		if (!db) throw new Error('Local database is not available');
		const passwordHash = await this.hashPassword(crypto.randomUUID());
		// A read-write transaction prevents duplicate workspaces from simultaneous tabs.
		const tx = db.transaction(this.USER_STORE, 'readwrite');
		const store = tx.objectStore(this.USER_STORE);
		const users: User[] = await store.getAll();
		let user = users.find((item) => item.isLocalWorkspace && !item.isGuest);
		if (!user) {
			const now = Date.now();
			user = {
				id: crypto.randomUUID(),
				username: 'Local Workspace',
				passwordHash,
				isLocalWorkspace: true,
				createdAt: now,
				lastLogin: now,
				color: generateRandomColor(false),
				colorLight: generateRandomColor(true),
			};
			await store.put(user);
		}
		await tx.done;
		this.currentUser = user;
		localStorage.setItem('texlyre-current-user', user.id);
		localStorage.removeItem('texstudio-profile-picker');
		return user;
	}
""" + s[end:]
old = "\t\tlocalStorage.removeItem('texlyre-current-user');\n\n\t\tif (!user) return;"
assert s.count(old) == 1
s = s.replace(old, "\t\tlocalStorage.removeItem('texlyre-current-user');\n\t\tlocalStorage.setItem('texstudio-profile-picker', 'true');\n\n\t\tif (!user) return;", 1)
p.write_text(s)

# Explicitly requesting the profile picker keeps regular account creation
# available. The default workspace button resumes the same local identity.
edit('src/components/auth/Login.tsx',
     'onClick={() => setShowGuestModal(true)}',
     'onClick={handleGuestSession}')
edit('src/components/auth/Login.tsx',
     "{t('Try as Guest')}",
     'Open local workspace (no account)')
edit('src/components/auth/Login.tsx',
     'setShowGuestModal(false);\n\t\t\tonLoginSuccess();',
     'setShowGuestModal(false);\n\t\t\tonLoginSuccess();\n\t\t\twindow.location.reload();')
edit('src/components/app/AuthApp.tsx',
     "<h1>{t('TeXlyre')}</h1>",
     '<h1>TeXStudio</h1>')

# Make this release invalidate the prior service-worker asset cache.
p = Path('package.json')
pkg = json.loads(p.read_text())
pkg['version'] = '0.14.9-texstudio.1'
p.write_text(json.dumps(pkg, indent='\t') + '\n')
