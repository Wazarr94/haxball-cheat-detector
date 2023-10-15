// @ts-check
import { join } from 'path';

// 1. Import the Skeleton plugin
import { skeleton } from '@skeletonlabs/tw-plugin';

/** @type {import('tailwindcss').Config} */
export default {
	content: [
		'./src/**/*.{html,js,svelte,ts}',
		join(require.resolve('@skeletonlabs/skeleton'), '../**/*.{html,js,svelte,ts}')
	],
	theme: {
		extend: {}
	},
	plugins: [
		skeleton({
			themes: {
				preset: [
					'skeleton',
					'crimson',
					'gold-nouveau',
					'hamlindigo',
					'modern',
					'rocket',
					'sahara',
					'seafoam',
					'vintage',
					'wintry'
				]
			}
		})
	]
};
