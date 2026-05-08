export default function useLocalStorage() {
	const store = (key: string, value: string | number | boolean | symbol) =>
		localStorage.setItem(key, value.toLocaleString());

	const remove = (key: string) => localStorage.removeItem(key);

	const clear = () => localStorage.clear();

	const get = (key: string) => localStorage.getItem(key);

	return { store, remove, clear, get };
}
