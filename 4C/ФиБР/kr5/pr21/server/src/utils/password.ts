import bcrypt from 'bcrypt';

export async function hashPassword(password: string) {
	const rounds = 10;
	return bcrypt.hash(password, rounds);
}

export async function verifyPassword(password: string, passwordHash: string) {
	return bcrypt.compare(password, passwordHash);
}
