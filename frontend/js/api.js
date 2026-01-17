/**
 * API Client for AI-Assisted Prompt Management System
 */

const API_BASE_URL = 'http://localhost:5001/api';

const TokenManager = {
    get() { return localStorage.getItem('access_token'); },
    set(token) { localStorage.setItem('access_token', token); },
    remove() { localStorage.removeItem('access_token'); },
    isValid() {
        const token = this.get();
        if (!token) return false;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp * 1000 > Date.now();
        } catch { return false; }
    }
};

const api = {
    // Default timeout in milliseconds
    REQUEST_TIMEOUT: 30000,

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const token = TokenManager.get();
        const headers = { 'Content-Type': 'application/json', ...options.headers };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), api.REQUEST_TIMEOUT);

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                signal: controller.signal
            });

            // Safe JSON parsing - handle non-JSON responses
            let data;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                const text = await response.text();
                data = { error: text || 'Unexpected response format' };
            }

            if (!response.ok) {
                if (response.status === 401) {
                    TokenManager.remove();
                    if (!window.location.pathname.includes('index.html')) {
                        window.location.href = 'index.html';
                    }
                }
                throw new Error(data.error || 'Request failed');
            }
            return data;
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timed out. Please try again.');
            }
            throw error;
        } finally {
            clearTimeout(timeoutId);
        }
    },

    auth: {
        async login(username, password) {
            const data = await api.request('/auth/login', {
                method: 'POST', body: JSON.stringify({ username, password })
            });
            if (data.access_token) TokenManager.set(data.access_token);
            return data;
        },
        async register(username, email, password, fullName) {
            const data = await api.request('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password, full_name: fullName })
            });
            if (data.access_token) TokenManager.set(data.access_token);
            return data;
        },
        async getProfile() { return api.request('/auth/me'); },
        logout() { TokenManager.remove(); window.location.href = 'index.html'; },
        isAuthenticated() { return TokenManager.isValid(); }
    },

    prompts: {
        async list(params = {}) {
            const qs = new URLSearchParams(params).toString();
            return api.request(qs ? `/prompts?${qs}` : '/prompts');
        },
        async get(id) { return api.request(`/prompts/${id}`); },
        async create(data) { return api.request('/prompts', { method: 'POST', body: JSON.stringify(data) }); },
        async update(id, data) { return api.request(`/prompts/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
        async delete(id) { return api.request(`/prompts/${id}`, { method: 'DELETE' }); },
        async getStats() { return api.request('/prompts/stats'); }
    },

    versions: {
        async list(promptId) { return api.request(`/prompts/${promptId}/versions`); },
        async get(id) { return api.request(`/versions/${id}`); },
        async setCurrent(id) { return api.request(`/versions/${id}/set-current`, { method: 'POST' }); },
        async delete(id) { return api.request(`/versions/${id}`, { method: 'DELETE' }); }
    },

    evaluation: {
        async evaluate(versionId) { return api.request(`/evaluate/${versionId}`, { method: 'POST' }); },
        async evaluateAll(promptId) { return api.request(`/evaluate/prompt/${promptId}`, { method: 'POST' }); },
        async getEvaluations(promptId) { return api.request(`/evaluations/${promptId}`); },
        async getRecommendation(promptId) { return api.request(`/recommend/${promptId}`); },
        // Read-only: Get existing evaluation without triggering AI or DB writes
        async getVersionEvaluation(versionId) { return api.request(`/evaluations/version/${versionId}`); },
        async quickEvaluate(text, type, domain) {
            return api.request('/quick-evaluate', {
                method: 'POST', body: JSON.stringify({ prompt_text: text, task_type: type, domain })
            });
        }
    },

    tags: {
        async list() { return api.request('/tags'); },
        async create(name, color) { return api.request('/tags', { method: 'POST', body: JSON.stringify({ name, color }) }); },
        async addToPrompt(promptId, tagId) {
            return api.request(`/tags/prompts/${promptId}/tags`, { method: 'POST', body: JSON.stringify({ tag_id: tagId }) });
        },
        async removeFromPrompt(promptId, tagId) {
            return api.request(`/tags/prompts/${promptId}/tags/${tagId}`, { method: 'DELETE' });
        }
    }
};

window.api = api;
window.TokenManager = TokenManager;
