export interface Product {
	id: string;
	title: string;
	category: string;
	description?: string;
	price: number;
	images?: string[];
	author_id: string;
}

export type ProductResponse = Product;
