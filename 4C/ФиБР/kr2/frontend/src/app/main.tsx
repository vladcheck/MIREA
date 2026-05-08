import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { BrowserRouter } from 'react-router';
import ApiWrapper from '@/features/api/ApiWrapper.tsx';
import SiteRoutes from './routes.tsx';

createRoot(document.getElementById('root')!).render(
	<StrictMode>
		<ApiWrapper>
			<BrowserRouter>
				<SiteRoutes />
			</BrowserRouter>
		</ApiWrapper>
	</StrictMode>,
);
