import { makeAutoObservable } from 'mobx';

export class CartStore {
	items: Map<string, number> = new Map();

	constructor() {
		makeAutoObservable(this);
		this.loadFromStorage();
	}

	addToCart(productId: string) {
		const current = this.items.get(productId) || 0;
		this.items.set(productId, current + 1);
		this.saveToStorage();
	}

	removeFromCart(productId: string) {
		const current = this.items.get(productId) || 0;
		if (current > 1) {
			this.items.set(productId, current - 1);
		} else {
			this.items.delete(productId);
		}
		this.saveToStorage();
	}

	getCartItems() {
		return this.items;
	}

	clearCart() {
		this.items.clear();
		this.saveToStorage();
	}

	private saveToStorage() {
		localStorage.setItem(
			'cart',
			JSON.stringify(Array.from(this.items.entries())),
		);
	}

	private loadFromStorage() {
		const stored = localStorage.getItem('cart');
		if (stored) {
			try {
				const parsed = JSON.parse(stored);
				this.items = new Map(parsed);
			} catch (e) {
				console.error('Failed to parse cart from storage', e);
			}
		}
	}
}

export const cartStore = new CartStore();
