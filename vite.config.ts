import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { config } from 'dotenv';

config();

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/api': {
				target:
					process.env.PROD_ENV == 'development'
						? 'http://localhost:8000'
						: 'https://haxball-cheat-detector-production.up.railway.app',

				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api/, '')
			}
		}
	}
});
