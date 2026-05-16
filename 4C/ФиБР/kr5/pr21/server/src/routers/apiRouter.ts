import { type Request, type Response, Router } from 'express';
import { getOk } from '../utils/requestHelpers';
import authRouter from './authRouter';
import productsRouter from './productsRouter';
import usersRouter from './usersRouter';

const apiRouter: Router = Router();
apiRouter.use('/api/auth', authRouter);
apiRouter.use('/api/users', usersRouter);
apiRouter.use('/api/products', productsRouter);

/*\
 * @swagger
 * /:
 *  get:
 *    summary: Возвращает OK
 *    description: Возвращает OK для проверки, что сервер запущен
 *    responses:
 *      200:
 *        description: Сервер работает
 */
apiRouter.get('/api/', async (_req: Request, res: Response) => {
	return getOk(res);
});

export default apiRouter;
