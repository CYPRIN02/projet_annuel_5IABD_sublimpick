import adapter from '@sveltejs/adapter-auto';

export default {
  kit: {
    adapter: adapter(),
    // Enable this if you're experiencing CSP issues with eval and inline scripts
    csp: {
      mode: 'auto', // or 'hash', depending on your needs
      directives: {
        'script-src': ['self', 'unsafe-eval', 'unsafe-inline'], // add 'unsafe-eval' and 'unsafe-inline' here if needed, but it's discouraged for security reasons
        'object-src': ['none'],
      },
    },
  },
};


// import adapter from '@sveltejs/adapter-auto';
// import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

// /** @type {import('@sveltejs/kit').Config} */
// const config = {
// 	// Consult https://kit.svelte.dev/docs/integrations#preprocessors
// 	// for more information about preprocessors
// 	preprocess: vitePreprocess(),

// 	kit: {
// 		// adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
// 		// If your environment is not supported, or you settled on a specific environment, switch out the adapter.
// 		// See https://kit.svelte.dev/docs/adapters for more information about adapters.
// 		adapter: adapter()
// 	}
// };

// export default config;
