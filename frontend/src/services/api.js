/**
 * AlgoMentor AI — Frontend API Client Foundation
 *
 * Provides a reusable fetch helper and health check for connecting to the
 * FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// ─── User Identity ───────────────────────────────────────────────────────────
// Hardcoded for Commit #2. Replace with real auth in a future milestone.
export const DEMO_USER_ID = 'demo-user';

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
            const err = new Error(`API Error ${response.status}: ${errorMessage}`);
            err.status = response.status;
            throw err;
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
    } catch {
        return false;
    }
}

// ─── Profile API ─────────────────────────────────────────────────────────────

/**
 * Fetch the saved StudentProfile for a user.
 *
 * Returns the full StudentProfileResponse object on success.
 * Throws with err.status === 404 when no profile exists yet.
 *
 * @param {string} userId
 * @returns {Promise<object>} StudentProfileResponse
 */
export async function getProfile(userId) {
    return apiFetch(`/api/users/${userId}/profile`);
}

/**
 * Save (create or replace) a StudentProfile for a user.
 *
 * @param {string} userId
 * @param {object} profile - Shape matching backend StudentProfile model
 * @returns {Promise<object>} StudentProfileResponse
 */
export async function saveProfile(userId, profile) {
    return apiFetch(`/api/users/${userId}/profile`, {
        method: 'PUT',
        body: JSON.stringify(profile),
    });
}

// ─── Schedule API ────────────────────────────────────────────────────────────

/**
 * Fetch the saved WeeklySchedule for a user.
 *
 * Returns the full WeeklyScheduleResponse object on success.
 * Throws with err.status === 404 when no schedule exists yet.
 *
 * @param {string} userId
 * @returns {Promise<object>} WeeklyScheduleResponse
 */
export async function getWeeklySchedule(userId) {
    return apiFetch(`/api/users/${userId}/weekly-schedule`);
}

/**
 * Save (create or replace) a WeeklySchedule for a user.
 *
 * @param {string} userId
 * @param {object} schedule - Shape matching backend WeeklySchedule model
 * @returns {Promise<object>} WeeklyScheduleResponse
 */
export async function saveWeeklySchedule(userId, schedule) {
    return apiFetch(`/api/users/${userId}/weekly-schedule`, {
        method: 'PUT',
        body: JSON.stringify(schedule),
    });
}

// ─── Daily Override API ───────────────────────────────────────────────────────

/**
 * Fetch a saved DailyOverride for a specific date.
 *
 * Returns the full DailyOverrideResponse object on success.
 * Throws with err.status === 404 when no override exists for that date.
 *
 * @param {string} userId
 * @param {string} date - ISO date string (e.g. '2026-06-17')
 * @returns {Promise<object>} DailyOverrideResponse
 */
export async function getDailyOverride(userId, date) {
    return apiFetch(`/api/users/${userId}/daily-overrides/${date}`);
}

/**
 * Save (create or replace) a DailyOverride for a specific date.
 *
 * @param {string} userId
 * @param {string} date - ISO date string (e.g. '2026-06-17')
 * @param {object} override - Shape matching backend DailyOverride model
 * @returns {Promise<object>} DailyOverrideResponse
 */
export async function saveDailyOverride(userId, date, override) {
    return apiFetch(`/api/users/${userId}/daily-overrides/${date}`, {
        method: 'PUT',
        body: JSON.stringify(override),
    });
}

/**
 * Delete a saved DailyOverride for a specific date.
 *
 * @param {string} userId
 * @param {string} date - ISO date string (e.g. '2026-06-17')
 * @returns {Promise<object>} DailyOverrideDeleteResponse
 */
export async function deleteDailyOverride(userId, date) {
    return apiFetch(`/api/users/${userId}/daily-overrides/${date}`, {
        method: 'DELETE',
    });
}

// ─── Smart Daily Plan API ─────────────────────────────────────────────────────

/**
 * Generate and fetch a Smart Daily Plan for a specific date.
 *
 * @param {string} userId
 * @param {string} date - ISO date string (e.g. '2026-06-17')
 * @returns {Promise<object>} DailyPlanResponse
 */
export async function getDailyPlan(userId, date) {
    return apiFetch(`/api/users/${userId}/daily-plan/${date}`);
}

// ─── SM-2 Revision API ────────────────────────────────────────────────────────

/**
 * Fetch the revision queue (due and upcoming topics) for a specific date.
 *
 * @param {string} userId
 * @param {string} asOfDate - ISO date string
 * @returns {Promise<object>} RevisionQueueResponse
 */
export async function getRevisionQueue(userId, asOfDate) {
    return apiFetch(`/api/users/${userId}/revision-queue/${asOfDate}`);
}

/**
 * Get user progress.
 *
 * @param {string} userId
 * @returns {Promise<object>} ProgressResponse
 */
export async function getUserProgress(userId) {
    return apiFetch(`/api/users/${userId}/progress`);
}

/**
 * Submit a topic review (recall quality 0-5) to update the SM-2 schedule.
 *
 * @param {string} userId
 * @param {string} topic
 * @param {number} quality - 0 (blackout) to 5 (perfect recall)
 * @param {string} reviewedOn - ISO date string
 * @returns {Promise<object>} TopicReviewResponse
 */
export async function submitTopicReview(userId, topic, quality, reviewedOn) {
    return apiFetch(`/api/users/${userId}/revision-reviews`, {
        method: 'POST',
        body: JSON.stringify({
            topic,
            quality,
            reviewed_on: reviewedOn
        }),
    });
}

// ─── Workspace IDE API ────────────────────────────────────────────────────────

/**
 * Fetch a recommended problem to solve in the IDE workspace.
 *
 * @returns {Promise<object>} Problem data
 */
export async function getWorkspaceProblem() {
    return apiFetch(`/api/workspace/problems/recommendation`);
}

/**
 * Fetch a specific problem by ID to solve in the IDE workspace.
 *
 * @param {string} problemId
 * @returns {Promise<object>} Problem data
 */
export async function getWorkspaceProblemById(problemId) {
    return apiFetch(`/api/workspace/problems/${problemId}`);
}

/**
 * Submit user code to the AI mentor for evaluation.
 *
 * @param {string} problemId
 * @param {string} code
 * @param {string} language
 * @returns {Promise<object>} EvaluateResponse
 */
export async function submitWorkspaceCode(problemId, code, language) {
    return apiFetch(`/api/workspace/evaluate`, {
        method: 'POST',
        body: JSON.stringify({
            problem_id: problemId,
            code,
            language
        }),
    });
}
