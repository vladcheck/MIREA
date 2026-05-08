import { cartStore } from './CartStore';

export default function useCart() {
	const addToCard = (id: string) => cartStore.addToCart(id);
	const removeFromCart = (id: string) => cartStore.removeFromCart(id);
	const getCartItems = () => cartStore.getCartItems();
	const clearCart = () => cartStore.clearCart();

	return { addToCard, getCartItems, removeFromCart, clearCart };
}
