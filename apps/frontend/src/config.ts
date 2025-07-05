
const config = {
    // API Base URL - change this based on your deployment
    API_URL: '', // For Docker with nginx proxy - use relative path

    // Static files URL
    get STATIC_URL() {
        return `${this.API_URL}/static`;
    },

    // Other configuration
    APP_NAME: 'AI News Sense',
    VERSION: '1.0.0'
};

export default config;