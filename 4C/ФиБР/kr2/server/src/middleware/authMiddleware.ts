import type { Request, Response } from 'express';
import type { JwtPayload } from 'jsonwebtoken';
import JwtSingleton from '../utils/jwt';
import { getUnauthorized } from '../utils/requestHelpers';

export default function authMiddleware(
	req: Request & { user?: JwtPayload },
	res: Response,
	next: Function,
) {
	const header = req.headers.authorization || '';
	const [scheme, token] = header.split(' ');
	if (scheme !== 'Bearer') {
		return getUnauthorized(res, "Wrong auth schema, expected 'Bearer'");
	}
	if (!token) {
		return getUnauthorized(res, 'Missing access token');
	}

	try {
		const payload = JwtSingleton.verify(token, 'access') as JwtPayload;
		req.user = payload;
		next();
	} catch (_err) {
		return getUnauthorized(res, 'Invalid or expired token');
	}
}
