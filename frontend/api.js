// API wrapper. Stub: return empty/default values. Phase 2+: implement real calls.

export async function getWorkflows(platform) {
  // Stub: return []
  return [];
}

export async function getSessions(platform, state = null) {
  // Stub: return []
  return [];
}

export async function getStats(platform) {
  // Stub: return default stats
  return { triggers: 0, messages: 0 };
}

export async function getPlatforms() {
  // Stub: return instagram enabled
  return [{ name: 'instagram', enabled: true }];
}

export async function pauseBot(platform = 'all') {
  // Stub: return ok
  return { status: 'paused', platform };
}

export async function resumeBot(platform = 'all') {
  // Stub: return ok
  return { status: 'running', platform };
}

export async function createWorkflow(data) {
  // Stub: return new workflow
  return { id: 1, ...data };
}
