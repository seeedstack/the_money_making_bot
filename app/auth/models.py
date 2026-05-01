import json
import os
from flask_login import UserMixin

_CREDS_FILE = os.path.join(os.path.dirname(__file__), "../../data/admin_creds.json")


class DashboardUser(UserMixin):
    """Single admin user. No DB table — credentials in .env + data/admin_creds.json."""
    id = "admin"

    def get_id(self):
        return self.id

    @staticmethod
    def creds_file_path() -> str:
        return _CREDS_FILE
