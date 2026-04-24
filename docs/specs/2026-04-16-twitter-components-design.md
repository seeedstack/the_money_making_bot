# Twitter Components Design

**Date:** 2026-04-16  
**Status:** Design for implementation  
**Scope:** TwitterClient, ReplyReader, DMSender, FollowChecker

---

## Overview

Implement 4 real Twitter integration components using Tweepy SDK (API v2). Each component raises exceptions on error; engine handles retry logic.

---

## TwitterClient

**Purpose:** Session factory. Maintain persistent Tweepy v2 client.

**Interface:**
```python
class TwitterClient:
    def __init__(self, account_id: int)
    def login() -> bool
    def get_tweet_replies(tweet_id: str) -> list[dict]
    def send_dm(recipient_id: str, text: str) -> bool
    def get_user(username: str) -> dict
```

**Behavior:**
- Load credentials from DB (account_id → api_key, api_secret, access_token, access_secret)
- Initialize Tweepy client on first login() call
- Keep session alive across calls (thread-safe)
- Auto-reconnect on session expire
- Raise exceptions on login/network/API errors

---

## ReplyReader

**Purpose:** Parse tweet replies into TriggerEvent objects.

**Interface:**
```python
class ReplyReader:
    def __init__(self, client: TwitterClient)
    def fetch(tweet_id: str) -> list[TriggerEvent]
```

**Behavior:**
- tweet_id = Twitter tweet ID (numeric)
- Fetch replies via client.get_tweet_replies()
- Parse each reply: extract username, text, timestamp
- Build TriggerEvent per reply
- Return list of all replies
- Raise on fetch/parse errors

---

## DMSender

**Purpose:** Send DMs via Twitter.

**Interface:**
```python
class DMSender:
    def __init__(self, client: TwitterClient)
    def send(recipient_id: str, text: str) -> bool
```

**Behavior:**
- recipient_id = Twitter user ID (numeric)
- Send DM via client.send_dm()
- Return True on success
- Raise on send failure

---

## FollowChecker

**Purpose:** Check follow status.

**Interface:**
```python
class FollowChecker:
    def __init__(self, client: TwitterClient)
    def is_following(username: str) -> FollowStatus
```

**Behavior:**
- Check if username follows account via client.get_user()
- Return FollowStatus: FOLLOWING | NOT_FOLLOWING | UNKNOWN
- Raise on check errors

---

## Architecture

```
TwitterAdapter
  ├── TwitterClient (session factory)
  │   └── Tweepy API v2 client (single persistent connection)
  │
  ├── ReplyReader (client) → read_triggers()
  ├── DMSender (client) → send_message()
  └── FollowChecker (client) → check_follow()
```

All 4 components share single TwitterClient instance.

---

## DB Dependencies

- **settings_repo:** Fetch account_<id>_key, account_<id>_secret, account_<id>_token, account_<id>_token_secret
- No writes from these components

---

## Testing

Unit tests mock TwitterClient. No real API calls.

---

## Tweepy API Specifics

- **v2 API:** Search, DM, user_info endpoints
- **Rate limits:** 15 min windows, per-endpoint caps (handled by rate_limiter.py)
- **Auth:** OAuth 1.0a (4 credential parts)

---
