/**
 * API Service
 * ===========
 * Service untuk komunikasi dengan backend API
 */

import axios from 'axios';

// Base URL untuk API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
    (config) => {
        // Add any auth headers here if needed
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response) => {
        return response.data;
    },
    (error) => {
        const errorMessage = error.response?.data?.detail || error.message || 'Terjadi kesalahan';
        return Promise.reject(new Error(errorMessage));
    }
);

// ==================== Health API ====================
export const healthAPI = {
    check: () => api.get('/health'),
    ready: () => api.get('/health/ready'),
    info: () => api.get('/health/info'),
};

// ==================== Recommendation API ====================
export const recommendationAPI = {
    /**
     * Get recommendations based on user preferences
     * @param {Object} specs - User specifications
     * @param {number} topK - Number of recommendations
     * @param {number} minSimilarity - Minimum similarity threshold
     */
    getRecommendations: (specs, topK = 10, minSimilarity = 0.3) =>
        api.post('/recommendations', {
            input_specs: specs,
            top_k: topK,
            min_similarity: minSimilarity,
        }),

    /**
     * Quick recommendation with minimal params
     */
    quickRecommendation: (params) =>
        api.post('/recommendations/quick', params),

    /**
     * Get list of all phones with pagination
     */
    getPhones: (params = {}) =>
        api.get('/recommendations/phones', { params }),

    /**
     * Get phone detail by ID
     */
    getPhoneDetail: (id) =>
        api.get(`/recommendations/phones/${id}`),

    /**
     * Get statistics
     */
    getStatistics: () =>
        api.get('/recommendations/statistics'),

    /**
     * Get available brands
     */
    getBrands: () =>
        api.get('/recommendations/brands'),

    /**
     * Get price ranges
     */
    getPriceRanges: () =>
        api.get('/recommendations/price-ranges'),
};

// ==================== Evaluation API ====================
export const evaluationAPI = {
    /**
     * Run evaluation with specified scenarios
     */
    runEvaluation: (config = {}) =>
        api.post('/evaluation/run', config),

    /**
     * Get previous evaluation results
     */
    getResults: () =>
        api.get('/evaluation/results'),

    /**
     * Get visualization data for charts
     */
    getVisualizationData: () =>
        api.get('/evaluation/visualization-data'),

    /**
     * Export results to file
     */
    exportResults: () =>
        api.post('/evaluation/export'),

    /**
     * Compare two scenarios
     */
    compareScenarios: (scenario1, scenario2) =>
        api.get(`/evaluation/compare/${scenario1}/${scenario2}`),
};

// ==================== Admin API ====================
export const adminAPI = {
    /**
     * Get current weights
     */
    getWeights: () =>
        api.get('/admin/weights'),

    /**
     * Update weights
     */
    updateWeights: (weights) =>
        api.put('/admin/weights', { weights }),

    /**
     * Reset weights to default
     */
    resetWeights: () =>
        api.post('/admin/weights/reset'),

    /**
     * Get weight presets
     */
    getWeightPresets: () =>
        api.get('/admin/weight-presets'),

    /**
     * Add new phone
     */
    addPhone: (phoneData) =>
        api.post('/admin/phones', phoneData),

    /**
     * Delete phone
     */
    deletePhone: (id) =>
        api.delete(`/admin/phones/${id}`),

    /**
     * Get dashboard data
     */
    getDashboard: () =>
        api.get('/admin/dashboard'),
};

export default api;
