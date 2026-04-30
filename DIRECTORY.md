### Module Structure

Each feature module follows this layout (using `app/auth/` as the reference):

```
app/<module>/
├── __init__.py     # Blueprint definition only — defines `bp`, then imports views and models
├── models.py       # SQLAlchemy models for this module
├── views.py        # Route handlers registered on `bp`
├── helpers/        # Pure helper functions (no Flask context dependencies)
└── workers/        # Background task workers
```

**`__init__.py`** — define the blueprint, then import views and models to trigger route/model registration:
```python
from flask import Blueprint
bp = Blueprint("auth", __name__)
from app.auth import views, models
```

**`models.py`** — SQLAlchemy models. Use `UUID(as_uuid=True)` PKs with `default=uuid.uuid4`. Include `deleted_at` / `deleted_by` columns for soft-delete. Place a `to_dict()` method on each model for serialization.

**`views.py`** — import `bp` from the module's `__init__`, use `AppMessages` for all response strings, and `bad_request` / `error_response` for all error returns. Always filter active records with `deleted_at=None`.

**Registering a new module** — add the blueprint in `app/__init__.py`:
```python
from app.<module> import bp as <module>_bp
app.register_blueprint(<module>_bp, url_prefix='/api/<module>')