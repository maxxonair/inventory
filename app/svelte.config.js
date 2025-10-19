import adapter from '@sveltejs/adapter-node';
export default {
  kit: { adapter: adapter(),
		    dev: {
								host: '0.0.0.0',
								port: 3000
    					}
	 }
};