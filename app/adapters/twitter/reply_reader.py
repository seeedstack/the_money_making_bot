# platforms/twitter/reply_reader.py

import logging
from datetime import datetime, timezone
from typing import Optional

from app.adapters.twitter.client import TwitterClient
from app.core.models.trigger import TriggerEvent
from app.core.models.platform import Platform

logger = logging.getLogger(__name__)


class ReplyReader:
    """Reads tweet replies and parses them into TriggerEvent objects."""

    def __init__(self, account_id: int):
        """Initialize ReplyReader with TwitterClient.

        Args:
            account_id: Account ID for Twitter authentication
        """
        self.account_id = account_id
        self.client = TwitterClient(account_id)

    def fetch(self, tweet_id: Optional[str]) -> list[TriggerEvent]:
        """Fetch tweet replies and parse into TriggerEvent list.

        Defensive parsing: uses .get() with defaults for missing dict keys.
        Input validation: returns empty list for None/empty tweet_id.

        Args:
            tweet_id: Tweet ID string to fetch replies for

        Returns:
            List of TriggerEvent objects parsed from replies.
            Empty list if tweet_id is None or empty.
        """
        # Input validation: reject None or empty tweet_id
        if not tweet_id:
            return []

        try:
            # Fetch raw reply data from Twitter API
            replies = self.client.get_tweet_replies(tweet_id)

            # Parse replies into TriggerEvent objects
            trigger_events = []
            for reply in replies:
                # Defensive dict access with .get() and defaults
                username = reply.get("username", "unknown")
                text = reply.get("text", "")
                created_at_str = reply.get("created_at")

                # Parse timestamp defensively
                try:
                    if created_at_str:
                        detected_at = datetime.fromisoformat(
                            created_at_str.replace("Z", "+00:00")
                        )
                    else:
                        # Default to now if timestamp missing
                        detected_at = datetime.now(timezone.utc)
                except (ValueError, AttributeError):
                    # Invalid timestamp format, use current time
                    detected_at = datetime.now(timezone.utc)

                # Create TriggerEvent
                event = TriggerEvent(
                    platform=Platform.TWITTER.value,
                    source_id=tweet_id,
                    username=username,
                    content=text,
                    matched_keyword="",  # Keyword matching done elsewhere
                    detected_at=detected_at
                )

                trigger_events.append(event)

            logger.info(
                f"Parsed {len(trigger_events)} replies from tweet {tweet_id}"
            )
            return trigger_events

        except Exception as e:
            logger.error(f"Failed to fetch/parse replies for tweet {tweet_id}: {e}")
            # Return empty list on error - let rate limiter/workers handle retry
            return []
