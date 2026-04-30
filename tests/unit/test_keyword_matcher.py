import pytest
from app.core.keyword_matcher import KeywordMatcher

def test_keyword_matcher_stub_returns_false():
    """Stub matcher should return False for now."""
    matcher = KeywordMatcher()
    result = matcher.match("hello world", "hello", "contains")
    assert result is False
