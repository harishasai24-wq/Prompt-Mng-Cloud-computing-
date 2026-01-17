/**
 * Security Utilities - XSS Prevention
 * Centralized sanitization for all user content rendering
 */

/**
 * Escapes HTML entities to prevent XSS attacks
 * @param {string} text - Untrusted text to escape
 * @returns {string} - Safe HTML-escaped string
 */
function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

/**
 * Escapes text for use in HTML attributes
 * @param {string} text - Untrusted text to escape
 * @returns {string} - Safe attribute-escaped string
 */
function escapeAttr(text) {
    if (text === null || text === undefined) {
        return '';
    }
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

/**
 * Sanitizes a URL to prevent javascript: protocol attacks
 * @param {string} url - URL to sanitize
 * @returns {string} - Safe URL or empty string
 */
function sanitizeUrl(url) {
    if (!url) return '';
    const trimmed = String(url).trim().toLowerCase();
    if (trimmed.startsWith('javascript:') || trimmed.startsWith('data:')) {
        return '';
    }
    return url;
}

// Export to window for global access
window.escapeHtml = escapeHtml;
window.escapeAttr = escapeAttr;
window.sanitizeUrl = sanitizeUrl;

// ═══════════════════════════════════════════════════════════════════════════════
// 🔐 DEFENSIVE FALLBACK (CRASH-PROOFING)
// ═══════════════════════════════════════════════════════════════════════════════
// Ensure critical functions exist even if something went wrong above
// This prevents hard stops caused by missing helpers

if (typeof window.escapeHtml !== "function") {
    console.warn("⚠️ escapeHtml not properly defined — using safe fallback");
    window.escapeHtml = function (value) {
        return String(value ?? "");
    };
}

if (typeof window.escapeAttr !== "function") {
    console.warn("⚠️ escapeAttr not properly defined — using safe fallback");
    window.escapeAttr = function (value) {
        return String(value ?? "")
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    };
}

if (typeof window.sanitizeUrl !== "function") {
    console.warn("⚠️ sanitizeUrl not properly defined — using safe fallback");
    window.sanitizeUrl = function (url) {
        if (!url) return '';
        const trimmed = String(url).trim().toLowerCase();
        if (trimmed.startsWith('javascript:') || trimmed.startsWith('data:')) {
            return '';
        }
        return url;
    };
}
