class _PlatformSettingsProxy:
    """Drop-in for old db.repositories.settings_repo — delegates to ORM when in app context."""

    def get(self, platform: str, key: str, default=None) -> str | None:
        try:
            from flask import current_app
            with current_app.app_context():
                from app.platforms.models import PlatformSettings
                return PlatformSettings.get(platform, key, default)
        except RuntimeError:
            return default

    def set(self, platform: str, key: str, value: str):
        try:
            from flask import current_app
            with current_app.app_context():
                from app.platforms.models import PlatformSettings
                PlatformSettings.set(platform, key, value)
        except RuntimeError:
            pass

    def get_all(self, platform: str) -> dict:
        try:
            from flask import current_app
            with current_app.app_context():
                from app.platforms.models import PlatformSettings
                rows = PlatformSettings.query.filter_by(platform=platform).all()
                return {r.key: r.value for r in rows}
        except RuntimeError:
            return {}


settings_repo = _PlatformSettingsProxy()
