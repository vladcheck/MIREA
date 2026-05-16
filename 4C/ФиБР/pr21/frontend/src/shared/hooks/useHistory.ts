import { useEffect, useState } from 'react';

export default function useHistory(): History | undefined {
	const [history, setHistory] = useState<History>();

	useEffect(() => {
		setHistory(window.history);
	}, []);

	return history;
}
