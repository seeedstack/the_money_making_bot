# platforms/twitter/client.py

import logging
import tweepy
from db.repositories.settings_repo import settings_repo
from platforms.twitter.errors import LoginError, APIError, NetworkError

logger = logging.getLogger(__name__)


class TwitterClient:
    """Tweepy v2 wrapper. Maintains ONE persistent session."""

    def __init__(self, account_id: int):
        """Initialize with account ID. Credentials loaded only at login time."""
        self.account_id = account_id
        self.cl = None  # Tweepy Client instance

    def login(self) -> bool:
        """Initialize Tweepy v2 client and authenticate with Twitter API.

        Loads 4-part credentials from DB only during login, never stores them in memory
        after authentication completes.
        Credentials: api_key, api_secret, access_token, access_token_secret
        """
        try:
            # Load 4-part credentials from DB only at login time
            api_key = settings_repo.get(
                platform="twitter",
                key=f"account_{self.account_id}_api_key"
            )
            api_secret = settings_repo.get(
                platform="twitter",
                key=f"account_{self.account_id}_api_secret"
            )
            access_token = settings_repo.get(
                platform="twitter",
                key=f"account_{self.account_id}_access_token"
            )
            access_secret = settings_repo.get(
                platform="twitter",
                key=f"account_{self.account_id}_access_secret"
            )

            self.cl = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )
            logger.info(f"Successfully logged in to Twitter with account {self.account_id}")
            return True
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning(f"Network error during login for account {self.account_id}: {e}")
            raise NetworkError(f"Network error during login: {e}")
        except Exception as e:
            logger.error(f"Login failed for account {self.account_id}: {e}")
            raise LoginError(f"Twitter login failed: {e}")

    @property
    def is_logged_in(self) -> bool:
        """Check if session is logged in."""
        return self.cl is not None

    def get_tweet_replies(self, tweet_id: str) -> list:
        """Get replies to a tweet. tweet_id = tweet ID string.

        Uses conversation_id to fetch all replies in the conversation,
        then fetches author info for each reply.
        """
        try:
            if not self.is_logged_in:
                self.login()

            # Search for replies using conversation_id
            query = f"conversation_id:{tweet_id}"
            response = self.cl.search_recent_tweets(
                query=query,
                tweet_fields=['author_id', 'created_at'],
                max_results=100
            )

            replies = []
            if response.data:
                for tweet in response.data:
                    # Fetch author username
                    try:
                        user_response = self.cl.get_user(id=tweet.author_id)
                        username = user_response.data.username if user_response.data else "unknown"
                    except Exception:
                        username = "unknown"

                    replies.append({
                        "id": tweet.id,
                        "username": username,
                        "author_id": tweet.author_id,
                        "text": tweet.text,
                        "created_at": tweet.created_at
                    })

            return replies
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning(f"Network error fetching replies for tweet {tweet_id}: {e}")
            raise NetworkError(f"Network error fetching replies: {e}")
        except Exception as e:
            logger.error(f"Failed to get replies for tweet {tweet_id}: {e}")
            raise APIError(f"Failed to get replies: {e}")

    def send_dm(self, recipient_id: str, text: str) -> bool:
        """Send DM. recipient_id = user ID or username."""
        try:
            if not self.is_logged_in:
                self.login()

            # Tweepy v2 create_direct_message requires recipient user ID
            self.cl.create_direct_message(
                dm_type="MessageCreate",
                conversationTypeId="ParticipantsIds",
                participantsIds=[recipient_id],
                mediaId=None,
                text=text
            )
            logger.info(f"DM sent to {recipient_id}")
            return True
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning(f"Network error sending DM to {recipient_id}: {e}")
            raise NetworkError(f"Network error sending DM: {e}")
        except Exception as e:
            logger.error(f"Failed to send DM to {recipient_id}: {e}")
            raise APIError(f"Failed to send DM: {e}")

    def get_user(self, username: str) -> dict:
        """Get user info dict including follow status.

        Returns dict with user info from Tweepy User object.
        """
        try:
            if not self.is_logged_in:
                self.login()

            user = self.cl.get_user(
                username=username,
                user_fields=['public_metrics', 'protected']
            )
            user_data = user.data
            return {
                "id": user_data.id,
                "username": user_data.username,
                "protected": user_data.protected,
                "followers_count": user_data.public_metrics.followers_count if user_data.public_metrics else 0
            }
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning(f"Network error fetching user info for {username}: {e}")
            raise NetworkError(f"Network error fetching user info: {e}")
        except Exception as e:
            logger.error(f"Failed to get user info for {username}: {e}")
            raise APIError(f"Failed to get user info: {e}")
