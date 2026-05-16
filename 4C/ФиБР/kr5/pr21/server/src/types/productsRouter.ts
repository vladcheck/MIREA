import type { Product as ProductEntity } from '../../../shared/types/Product';

export type ProductRequestBody = {
	[K in keyof ProductEntity]: string;
} & {
	author_id: string;
};
