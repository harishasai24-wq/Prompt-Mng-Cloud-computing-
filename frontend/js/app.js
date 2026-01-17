/**
 * Main Application Logic
 */

// ═══════════════════════════════════════════════════════════════════════════════
// 🔐 GLOBAL UI ERROR GUARD (PREVENTS SILENT CRASHES)
// ═══════════════════════════════════════════════════════════════════════════════
window.onerror = function (message, source, lineno, colno, error) {
    console.error("Global UI Error:", { message, source, lineno, colno, error });

    if (typeof showToast === "function") {
        showToast(
            "A UI error occurred. The app is still running. Check console.",
            "error"
        );
    }
    // Return false to allow default error handling (shows in console)
    return false;
};

// Handle unhandled promise rejections
window.onunhandledrejection = function (event) {
    console.error("Unhandled Promise Rejection:", event.reason);

    if (typeof showToast === "function") {
        showToast(
            "An async error occurred. Check console for details.",
            "error"
        );
    }
};

// ═══════════════════════════════════════════════════════════════════════════════
// 🔍 DEPENDENCY CHECK ON PAGE LOAD
// ═══════════════════════════════════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", () => {
    const requiredGlobals = ["api", "escapeHtml", "TokenManager"];

    const missing = requiredGlobals.filter(
        g => typeof window[g] === "undefined"
    );

    if (missing.length > 0) {
        console.error("⚠️ Missing required globals:", missing);
        console.error("Check that all script files are loaded in correct order:");
        console.error("  1. sanitize.js (provides escapeHtml)");
        console.error("  2. api.js (provides api, TokenManager)");
        console.error("  3. app.js (provides UI utilities)");

        // Try to show toast if available, otherwise alert
        if (typeof showToast === "function") {
            showToast(
                "App misconfiguration detected. Check console.",
                "error"
            );
        } else {
            alert("App initialization error. Missing: " + missing.join(", "));
        }
    }
});

// Toast notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Loading state
function setLoading(element, loading) {
    if (loading) {
        element.disabled = true;
        element.dataset.originalText = element.textContent;
        element.innerHTML = '<span class="loading-spinner"></span>';
    } else {
        element.disabled = false;
        element.textContent = element.dataset.originalText;
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Get score class
function getScoreClass(score) {
    if (score >= 75) return 'score-high';
    if (score >= 50) return 'score-medium';
    return 'score-low';
}

// Auth guard
function requireAuth() {
    if (!api.auth.isAuthenticated()) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// Modal helpers
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modals on overlay click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
    }
});

// Close modals on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
    }
});

// Render prompt card (XSS-safe)
function renderPromptCard(prompt) {
    const currentVersion = prompt.current_version;
    const previewText = currentVersion
        ? currentVersion.prompt_text.substring(0, 150) + '...'
        : 'No content';

    // Escape all user-controlled content
    const safeTitle = escapeHtml(prompt.title);
    const safePreview = escapeHtml(previewText);
    const safeTaskType = escapeHtml(prompt.task_type);
    const safeDomain = prompt.domain ? escapeHtml(prompt.domain) : '';

    // Escape tag content
    const safeTags = (prompt.tags || []).map(t => {
        const safeName = escapeHtml(t.name);
        const safeColor = escapeAttr(t.color || '#6366f1');
        return `<span class="tag" style="border-color: ${safeColor}40; background: ${safeColor}20; color: ${safeColor}">${safeName}</span>`;
    }).join('');

    return `
        <div class="prompt-card" onclick="viewPrompt(${parseInt(prompt.id, 10) || 0})">
            <div class="prompt-card-header">
                <div>
                    <h3 class="prompt-card-title">${safeTitle}</h3>
                    <div class="prompt-card-meta">
                        <span>${safeTaskType}</span>
                        ${safeDomain ? `<span>• ${safeDomain}</span>` : ''}
                    </div>
                </div>
                <span class="badge badge-primary">v${parseInt(prompt.version_count, 10) || 0}</span>
            </div>
            <p class="prompt-card-preview">${safePreview}</p>
            <div class="prompt-card-footer">
                <div class="prompt-card-tags">${safeTags}</div>
                <span class="text-muted">${formatDate(prompt.updated_at)}</span>
            </div>
        </div>
    `;
}

// Render version item (XSS-safe)
function renderVersionItem(version, promptId) {
    const safeNotes = escapeHtml(version.change_notes || 'No notes');
    const versionNum = parseInt(version.version_number, 10) || 0;
    const versionId = parseInt(version.id, 10) || 0;
    const safePromptId = parseInt(promptId, 10) || 0;

    return `
        <div class="version-item ${version.is_current ? 'current' : ''}">
            <div class="version-number">v${versionNum}</div>
            <div class="version-info">
                <h4>Version ${versionNum} ${version.is_current ? '<span class="badge badge-success">Current</span>' : ''}</h4>
                <p>${safeNotes} • ${formatDate(version.created_at)}</p>
            </div>
            <div class="version-actions">
                ${!version.is_current ? `<button class="btn btn-sm btn-secondary" onclick="setCurrentVersion(${versionId}, ${safePromptId})">Set Current</button>` : ''}
                <button class="btn btn-sm btn-primary" onclick="evaluateVersion(${versionId})">Evaluate</button>
            </div>
        </div>
    `;
}

// Render score display
function renderScoreDisplay(evaluation) {
    return `
        <div class="score-breakdown">
            <div class="score-item">
                <div class="score-item-value ${getScoreClass(evaluation.clarity_score)}">${evaluation.clarity_score}</div>
                <div class="score-item-label">Clarity</div>
            </div>
            <div class="score-item">
                <div class="score-item-value ${getScoreClass(evaluation.relevance_score)}">${evaluation.relevance_score}</div>
                <div class="score-item-label">Relevance</div>
            </div>
            <div class="score-item">
                <div class="score-item-value ${getScoreClass(evaluation.length_score)}">${evaluation.length_score}</div>
                <div class="score-item-label">Length</div>
            </div>
        </div>
        <div class="mt-md" style="text-align: center;">
            <div class="score-item-value ${getScoreClass(evaluation.final_score)}" style="font-size: 2.5rem;">${evaluation.final_score}</div>
            <div class="score-item-label">Final Score</div>
        </div>
    `;
}

window.showToast = showToast;
window.setLoading = setLoading;
window.formatDate = formatDate;
window.getScoreClass = getScoreClass;
window.requireAuth = requireAuth;
window.openModal = openModal;
window.closeModal = closeModal;
window.renderPromptCard = renderPromptCard;
window.renderVersionItem = renderVersionItem;
window.renderScoreDisplay = renderScoreDisplay;
