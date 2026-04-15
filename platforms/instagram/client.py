# platforms/instagram/client.py

import logging
import re
from instagrapi import Client
from db.repositories.settings_repo import settings_repo
from platforms.instagram.errors import LoginError, APIError, NetworkError

logger = logging.getLogger(__name__)


class InstagramClient:
    """Instagrapi wrapper. Maintains ONE persistent session."""

    def __init__(self, account_id: int):
        """Initialize with account ID. Credentials loaded only at login time."""
        self.account_id = account_id
        self.cl = None  # Instagrapi Client instance

    def login(self) -> bool:
        """Initialize Instagrapi client and login to Instagram.

        Loads credentials from DB only during login, never stores them in memory
        after authentication completes.
        """
        try:
            # Load credentials from DB only at login time (scoped scope)
            username = settings_repo.get(
                platform="instagram",
                key=f"account_{self.account_id}_user"
            )
            password = settings_repo.get(
                platform="instagram",
                key=f"account_{self.account_id}_pass"
            )

            self.cl = Client()
            self.cl.login(username, password)
            logger.info(f"Successfully logged in to Instagram with account {self.account_id}")
            return True
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning(f"Network error during login for account {self.account_id}: {e}")
            raise NetworkError(f"Network error during login: {e}")
        except Exception as e:
            logger.error(f"Login failed for account {self.account_id}: {e}")
            raise LoginError(f"Instagram login failed: {e}")

    @property
    def is_logged_in(self) -> bool:
        """Check if session is logged in."""
        return self.cl is not None

    def get_comments(self, source_id: str) -> list:
        """Get comments from post. source_id = post URL or ID."""
        try:
            if not self.is_logged_in:
                self.login()

            # Parse post ID from URL if needed
            post_id = self._extract_post_id(source_id)

            # Fetch media info from Instagram
            media = self.cl.media_info(post_id)
            comments = []

            # Parse comments from media response
            if hasattr(media, 'comments') and media.comments:
                for comment in media.comments:
                    comments.append({
                        "username": comment.user.username,
                        "text": comment.text,
                        "timestamp": comment.taken_at
                    })

            return comments
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning(f"Network error fetching comments for source {source_id}: {e}")
            raise NetworkError(f"Network error fetching comments: {e}")
        except ValueError as e:
            logger.error(f"Invalid source_id format: {source_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get comments from {source_id}: {e}")
            raise APIError(f"Failed to get comments: {e}")

    def send_dm(self, recipient_id: str, text: str) -> bool:
        """Send DM. recipient_id = user ID or username."""
        try:
            if not self.is_logged_in:
                self.login()

            self.cl.send_direct_message(recipient_id, text)  # instagrapi method name
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

        Returns dict with user info from Instagrapi User object.
        The 'follower' field indicates if the user follows the authenticated account.
        """
        try:
            if not self.is_logged_in:
                self.login()

            user = self.cl.user_info_by_username(username)
            return {
                "id": user.id,
                "username": user.username,
                "is_private": user.is_private,
                "follower_count": user.follower_count,
                "follower": user.follower if hasattr(user, 'follower') else None
            }
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning(f"Network error fetching user info for {username}: {e}")
            raise NetworkError(f"Network error fetching user info: {e}")
        except Exception as e:
            logger.error(f"Failed to get user info for {username}: {e}")
            raise APIError(f"Failed to get user info: {e}")

    def _extract_post_id(self, source_id: str) -> str:
        """Extract post ID from URL or return as-is if already ID.

        Supports Instagram URLs: /p/, /reel/, /tv/, /stories/
        If already looks like a post ID, returns as-is.
        Raises ValueError for invalid URL formats.
        """
        # If already looks like an ID (alphanumeric, underscores, dashes), return as-is
        if re.match(r"^[a-zA-Z0-9_-]+$", source_id):
            return source_id

        # Try to extract from Instagram URL
        match = re.search(r"/(?:p|reel|tv|stories)/([a-zA-Z0-9_-]+)", source_id)
        if match:
            return match.group(1)

        # URL doesn't match expected format
        raise ValueError(f"Invalid Instagram URL format: {source_id}")
