-- Core tables
CREATE TABLE IF NOT EXISTS workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    name TEXT NOT NULL,
    trigger_keyword TEXT NOT NULL,
    source_id TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT 1,
    match_mode TEXT DEFAULT 'contains',
    link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    step_type TEXT NOT NULL,
    message_template TEXT,
    send_if TEXT,
    delay_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);

CREATE TABLE IF NOT EXISTS trigger_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    source_id TEXT NOT NULL,
    username TEXT NOT NULL,
    content TEXT NOT NULL,
    matched_workflow_id INTEGER,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS message_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    username TEXT NOT NULL,
    workflow_id INTEGER NOT NULL,
    current_step INTEGER DEFAULT 0,
    follow_status TEXT DEFAULT 'NOT_FOLLOWING',
    state TEXT DEFAULT 'STEP_RUNNING',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_action_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);

CREATE TABLE IF NOT EXISTS pending_follow_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    session_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    check_after TIMESTAMP NOT NULL,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES message_sessions(id)
);

CREATE TABLE IF NOT EXISTS platform_settings (
    platform TEXT NOT NULL PRIMARY KEY,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS platform_daily_counts (
    platform TEXT NOT NULL,
    date TEXT NOT NULL,
    messages_sent INTEGER DEFAULT 0,
    triggers_matched INTEGER DEFAULT 0,
    PRIMARY KEY (platform, date)
);

-- Instagram-specific tables
CREATE TABLE IF NOT EXISTS instagram_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_encrypted TEXT NOT NULL,
    salt TEXT NOT NULL,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS instagram_rate_windows (
    account_id INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    message_count INTEGER DEFAULT 1,
    PRIMARY KEY (account_id, timestamp),
    FOREIGN KEY (account_id) REFERENCES instagram_accounts(id)
);

CREATE TABLE IF NOT EXISTS instagram_session_cache (
    account_id INTEGER NOT NULL,
    session_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (account_id),
    FOREIGN KEY (account_id) REFERENCES instagram_accounts(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_workflows_platform ON workflows(platform);
CREATE INDEX IF NOT EXISTS idx_trigger_scans_platform ON trigger_scans(platform);
CREATE INDEX IF NOT EXISTS idx_message_sessions_platform ON message_sessions(platform);
