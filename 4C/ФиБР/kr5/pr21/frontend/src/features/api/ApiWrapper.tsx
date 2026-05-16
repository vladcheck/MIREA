import { type PropsWithChildren, useState } from 'react';
import ApiContext from './ApiContext';
import apiFacade from './ApiFacade';

export default function ApiWrapper({ children }: PropsWithChildren) {
	const [api] = useState(apiFacade);

	return <ApiContext value={{ api }}>{children}</ApiContext>;
}
