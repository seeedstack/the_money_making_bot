# Twitter Components Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development to execute task-by-task.

**Goal:** Implement 4 real Twitter components (TwitterClient, ReplyReader, DMSender, FollowChecker) using Tweepy API v2.

**Architecture:** Client maintains persistent Tweepy session. 3 helpers wrap client calls, parse responses, raise exceptions. All integrated into TwitterAdapter.

**Tech Stack:** Tweepy v4 (SDK), pytest (tests), mock (test mocks)

---

## Task 1: Error Classes

**Files:** Create `platforms/twitter/errors.py`

- [ ] Create TwitterError, LoginError, APIError, NetworkError (same pattern as Instagram)

---

## Task 2: TwitterClient

**Files:** Create `tests/unit/platforms/twitter/test_client.py`, modify `platforms/twitter/client.py`

- [ ] Write 15 failing tests (login, get_tweet_replies, send_dm, get_user, credential loading, error cases)
- [ ] Implement TwitterClient with persistent Tweepy session
- [ ] Load 4-part credentials from DB (key, secret, token, token_secret)
- [ ] Implement lazy login, auto-reconnect
- [ ] Add logging, error handling (LoginError, APIError, NetworkError)
- [ ] Run tests, all pass

---

## Task 3: ReplyReader

**Files:** Create `tests/unit/platforms/twitter/test_reply_reader.py`, modify `platforms/twitter/reply_reader.py`

- [ ] Write 6 failing tests (fetch replies, empty, malformed, missing fields, client error)
- [ ] Implement ReplyReader.fetch() with defensive dict access
- [ ] Input validation (tweet_id format)
- [ ] Add logging, tests pass

---

## Task 4: DMSender

**Files:** Create `tests/unit/platforms/twitter/test_dm_sender.py`, modify `platforms/twitter/dm_sender.py`

- [ ] Write 4 failing tests (send success, API error, network error, client call)
- [ ] Implement DMSender.send() as simple wrapper
- [ ] Error propagation, tests pass

---

## Task 5: FollowChecker

**Files:** Create `tests/unit/platforms/twitter/test_follow_checker.py`, modify `platforms/twitter/follow_checker.py`

- [ ] Write 5 failing tests (following, not following, unknown, error, client call)
- [ ] Implement FollowChecker.is_following() with FollowStatus enum
- [ ] Handle missing 'follows' field (return UNKNOWN), tests pass

---

## Task 6: Integration (TwitterAdapter)

**Files:** Modify `platforms/twitter/adapter.py`, create `tests/unit/platforms/twitter/test_adapter.py`

- [ ] Create TwitterAdapter.__init__() with all 4 components
- [ ] Implement read_triggers() → ReplyReader.fetch()
- [ ] Implement send_message() → DMSender.send()
- [ ] Implement check_follow() → FollowChecker.is_following()
- [ ] Write 14 integration tests, all pass
- [ ] Update platforms/registry.py to register TwitterAdapter

---

## Task 7: Verify Tests

**Files:** None (verification only)

- [ ] Run `pytest tests/unit/platforms/twitter/ -v`, all tests pass
- [ ] Check coverage >90%
- [ ] Verify all imports work
- [ ] Final count: expect ~50 Twitter tests passing

---

## Execution Model

Same as Instagram:
- TDD: test fails → implement → test passes → commit (no commits per user request)
- Spec + code quality reviews per task
- Subagent-driven: fresh implementer per task, 2-stage review (spec, quality)
- Parallel where possible, but tasks are sequential (each builds on prior)

---
