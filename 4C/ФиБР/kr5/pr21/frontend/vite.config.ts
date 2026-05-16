import path from 'node:path';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react-swc';
import { defineConfig } from 'vite';

// https://vite.dev/config/
export default defineConfig({
	root: '.',
	publicDir: 'public',
	plugins: [react(), tailwindcss()],
	preview: {
		port: 3001,
		cors: true,
	},
	build: {
		sourcemap: true,
		rollupOptions: {
			output: {
				manualChunks: {
					axios: ['axios'],
					react: ['react', 'react-dom', 'react-router', 'react-toastify'],
					tailwindcss: ['tailwindcss', 'tailwind-merge'],
				},
			},
		},
	},
	server: {
		port: 3001,
		cors: true,
	},
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src'),
			'@root-shared': path.resolve(__dirname, '../shared/'),
			'@public/*': path.resolve(__dirname, 'public/'),
		},
	},
});
