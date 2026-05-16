import { createContext } from 'react';
import apiFacade from './ApiFacade';

const ApiContext = createContext<{
	api?: typeof apiFacade;
}>({ api: apiFacade });
export default ApiContext;
