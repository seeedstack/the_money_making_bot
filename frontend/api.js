const BASE_URL = '/api';

async function fetch_(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    return response.json();
}

// Workflows
export async function getWorkflows(platform) {
    return fetch_(`${BASE_URL}/workflows?platform=${platform}`).then(r => r.workflows || []);
}

export async function createWorkflow(platform, data) {
    return fetch_(`${BASE_URL}/workflows?platform=${platform}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({...data, platform})
    });
}

export async function updateWorkflow(platform, id, data) {
    return fetch_(`${BASE_URL}/workflows/${id}?platform=${platform}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

export async function deleteWorkflow(platform, id) {
    return fetch_(`${BASE_URL}/workflows/${id}?platform=${platform}`, {method: 'DELETE'});
}

export async function toggleWorkflow(platform, id) {
    return fetch_(`${BASE_URL}/workflows/${id}/toggle?platform=${platform}`, {method: 'POST'});
}

// Sessions
export async function getSessions(platform, state = null) {
    const url = state
        ? `${BASE_URL}/sessions?platform=${platform}&state=${state}`
        : `${BASE_URL}/sessions?platform=${platform}`;
    return fetch_(url).then(r => ({sessions: r.sessions || [], count: r.sessions?.length || 0}));
}

export async function getSession(platform, id) {
    return fetch_(`${BASE_URL}/sessions/${id}?platform=${platform}`);
}

// Stats
export async function getStats(platform) {
    return fetch_(`${BASE_URL}/stats?platform=${platform}`);
}

// Platforms
export async function getPlatforms() {
    return fetch_(`${BASE_URL}/platforms`).then(r => r.platforms || []);
}

// Checks
export async function getPendingChecks(platform) {
    return fetch_(`${BASE_URL}/pending-checks?platform=${platform}`).then(r => ({
        checks: r.checks || [],
        count: r.count || 0
    }));
}

export async function forceCheck(platform, id) {
    return fetch_(`${BASE_URL}/pending-checks/${id}/force?platform=${platform}`, {method: 'POST'});
}

export async function abandonCheck(platform, id) {
    return fetch_(`${BASE_URL}/pending-checks/${id}/abandon?platform=${platform}`, {method: 'POST'});
}

// Bot Control
export async function pauseBot(platform = 'all') {
    return fetch_(`${BASE_URL}/bot/pause?platform=${platform}`, {method: 'POST'});
}

export async function resumeBot(platform = 'all') {
    return fetch_(`${BASE_URL}/bot/resume?platform=${platform}`, {method: 'POST'});
}

export async function restartBot(platform = 'all') {
    return fetch_(`${BASE_URL}/bot/restart?platform=${platform}`, {method: 'POST'});
}
