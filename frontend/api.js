const BASE_URL = '/api';

async function fetch_(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        if (response.status === 401) {
            window.location.href = '/auth/login';
            return;
        }
        const err = new Error(`API Error: ${response.status}`);
        err.status = response.status;
        throw err;
    }
    return response.json();
}

window.api = {
    // Workflows
    getWorkflows(platform) {
        return fetch_(`${BASE_URL}/workflows?platform=${platform}`)
            .then(r => ({ workflows: r.workflows || [] }));
    },
    createWorkflow(platform, data) {
        return fetch_(`${BASE_URL}/workflows?platform=${platform}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...data, platform })
        });
    },
    updateWorkflow(platform, id, data) {
        return fetch_(`${BASE_URL}/workflows/${id}?platform=${platform}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    },
    deleteWorkflow(platform, id) {
        return fetch_(`${BASE_URL}/workflows/${id}?platform=${platform}`, { method: 'DELETE' });
    },
    toggleWorkflow(platform, id) {
        return fetch_(`${BASE_URL}/workflows/${id}/toggle?platform=${platform}`, { method: 'POST' });
    },

    // Sessions
    getSessions(platform, state = null) {
        const url = state
            ? `${BASE_URL}/sessions?platform=${platform}&state=${state}`
            : `${BASE_URL}/sessions?platform=${platform}`;
        return fetch_(url).then(r => ({
            sessions: r.sessions || [],
            count: r.sessions?.length || 0
        }));
    },
    getSession(id, platform) {
        return fetch_(`${BASE_URL}/sessions/${id}?platform=${platform}`);
    },
    getSessionTrace(id, platform) {
        return fetch_(`${BASE_URL}/sessions/${id}/trace?platform=${platform}`);
    },

    // Stats
    getStats(platform) {
        return fetch_(`${BASE_URL}/stats?platform=${platform}`);
    },

    // Platforms
    getPlatforms() {
        return fetch_(`${BASE_URL}/platforms`)
            .then(r => ({ platforms: r.platforms || [] }));
    },
    enablePlatform(name) {
        return fetch_(`${BASE_URL}/platforms/${name}/enable`, { method: 'POST' });
    },
    disablePlatform(name) {
        return fetch_(`${BASE_URL}/platforms/${name}/disable`, { method: 'POST' });
    },

    // Checks
    getPendingChecks(platform) {
        return fetch_(`${BASE_URL}/pending-checks?platform=${platform}`)
            .then(r => ({ checks: r.checks || [], count: r.count || 0 }));
    },
    forceCheck(id) {
        return fetch_(`${BASE_URL}/pending-checks/${id}/force`, { method: 'POST' });
    },
    abandonCheck(id) {
        return fetch_(`${BASE_URL}/pending-checks/${id}/abandon`, { method: 'POST' });
    },

    // Bot Control
    pauseBot(platform = 'all') {
        return fetch_(`${BASE_URL}/bot/pause?platform=${platform}`, { method: 'POST' });
    },
    resumeBot(platform = 'all') {
        return fetch_(`${BASE_URL}/bot/resume?platform=${platform}`, { method: 'POST' });
    },
    restartBot(platform = 'all') {
        return fetch_(`${BASE_URL}/bot/restart?platform=${platform}`, { method: 'POST' });
    }
};
