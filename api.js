/**
 * api.js
 * ------
 * Shared API helper for Anumati Hostel Leave Management.
 *
 * Auth approach (no JWT):
 *   - Login returns { user_id, email, role, mobile }
 *   - user_id is stored in localStorage as `{role}_user_id`
 *   - Every protected API call sends the header: X-User-Id: <user_id>
 *
 * Backend: http://127.0.0.1:8000
 * Swagger: http://127.0.0.1:8000/docs
 */

const BASE_URL = 'http://127.0.0.1:8000';

// ── User Storage Helpers ──────────────────────────────────────────────────────

/** Save user info to localStorage after login */
function saveUser(role, userData) {
    localStorage.setItem(`${role}_user_id`,    String(userData.user_id));
    localStorage.setItem(`${role}_user_email`, userData.email);
    if (userData.mobile) {
        localStorage.setItem(`${role}_user_mobile`, userData.mobile);
    }
}

/** Get the stored user_id for a role (used as X-User-Id header) */
function getUserId(role) {
    return localStorage.getItem(`${role}_user_id`);
}

/** Get the stored email for a role */
function getUserEmail(role) {
    return localStorage.getItem(`${role}_user_email`);
}

/** Clear all stored data for a role on logout */
function clearUser(role) {
    localStorage.removeItem(`${role}_user_id`);
    localStorage.removeItem(`${role}_user_email`);
    localStorage.removeItem(`${role}_user_mobile`);
}

// ── Auth Guard ────────────────────────────────────────────────────────────────
/**
 * Call at the top of every dashboard page.
 * Redirects to the login page if no user_id is found for that role.
 */
function redirectIfNotLoggedIn(role) {
    if (!getUserId(role)) {
        window.location.href = `${role}_login.html`;
    }
}

// ── Core API Request ──────────────────────────────────────────────────────────
/**
 * @param {string} method   - HTTP method (GET, POST, PATCH, etc.)
 * @param {string} path     - API path, e.g. '/auth/student/login'
 * @param {object|null} body     - JSON body (optional)
 * @param {string|null} userId   - User ID to send as X-User-Id header (optional)
 * @returns {Promise<object>}    - Parsed JSON response
 * @throws {Error} with message from backend on non-2xx
 */
async function apiRequest(method, path, body = null, userId = null) {
    const headers = { 'Content-Type': 'application/json' };

    // Send user_id as a simple header — no JWT Bearer token needed
    if (userId !== null) {
        headers['X-User-Id'] = String(userId);
    }

    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(`${BASE_URL}${path}`, options);

    // Parse JSON (works for both success and error responses)
    let data;
    try {
        data = await response.json();
    } catch {
        data = { detail: 'Server returned an unexpected response.' };
    }

    if (!response.ok) {
        // FastAPI returns { detail: "..." } on errors
        const msg = typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail);
        throw new Error(msg);
    }

    return data;
}

// ── Toast Notification ────────────────────────────────────────────────────────
/**
 * Shows a slide-in toast notification at the bottom-right.
 * @param {string} message
 * @param {'success'|'error'} type
 */
function showToast(message, type = 'success') {
    const existing = document.getElementById('anumati-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'anumati-toast';
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add('toast-visible'));

    setTimeout(() => {
        toast.classList.remove('toast-visible');
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}

// ── Inline Error Helper ───────────────────────────────────────────────────────
function setError(elementId, message) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.style.display = message ? 'block' : 'none';
}

// ── Loading Button Helper ─────────────────────────────────────────────────────
function setButtonLoading(btn, loading, originalText = 'Submit') {
    if (loading) {
        btn.disabled = true;
        btn.innerHTML = '<span class="btn-spinner"></span> Loading...';
    } else {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// ── Logout ────────────────────────────────────────────────────────────────────
function logout(role) {
    clearUser(role);
    window.location.href = `${role}_login.html`;
}
