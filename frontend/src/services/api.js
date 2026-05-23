/**
 * AlgoMentor AI — Frontend API Client Foundation
 *
 * Provides a reusable fetch helper and health check for connecting to the
 * FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Generic fetch wrapper for API requests.
 * @param {string} endpoint - The API endpoint starting with '/' (e.g., '/health')
 * @param {RequestInit} options - Standard fetch options (method, headers, body, etc.)
 * @returns {Promise<any>} JSON response data
 * @throws {Error} If the server is unreachable or returns a non-2xx status
 */
export async function apiFetch(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        // Always parse JSON if there's content, even for errors
        const hasContent = response.headers.get('content-type')?.includes('application/json');
        const data = hasContent ? await response.json() : null;

        if (!response.ok) {
            // Throw an error with the details from the backend if possible
            const errorMessage = data?.detail || response.statusText || 'Unknown API Error';
            throw new Error(`API Error ${response.status}: ${errorMessage}`);
        }

        return data;
    } catch (error) {
        // Log the error cleanly and re-throw for the caller to handle
        console.error(`[API Fetch Failed] ${options.method || 'GET'} ${url}`, error);
        throw error;
    }
}

/**
 * Checks if the backend is reachable and healthy.
 * @returns {Promise<boolean>} true if healthy, false otherwise
 */
export async function checkBackendHealth() {
    try {
        const data = await apiFetch('/health');
        return data?.status === 'healthy';
    } catch (error) {
        return false;
    }
}
