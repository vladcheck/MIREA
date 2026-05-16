/**
 * A custom hook that provides a function for "hard" navigation.
 * Instead of SPA soft-navigation, it triggers a full browser reload to the target path.
 * This is useful for ensuring a clean application state on redirect.
 */
export function useHardNavigate() {
	const hardNavigate = (path: string | number) => {
		if (typeof path === 'number') {
			window.history.go(path);
			return;
		}

		// Ensure the path is an absolute URL or a relative path
		const targetUrl = path.startsWith('http')
			? path
			: `${window.location.origin}${path.startsWith('/') ? '' : '/'}${path}`;

		window.location.assign(targetUrl);
	};

	return hardNavigate;
}
