/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect } from 'react';

export default function useDebouncer(
	cb: () => unknown,
	ms: number,
	dependencies: unknown[],
): void {
	useEffect(() => {
		const debouncer = setTimeout(cb, ms);
		return () => clearTimeout(debouncer);
	}, [cb, ms, ...dependencies]);
}
