import pytest
from app.workflows.models import Workflow
from app.extensions import db


def test_workflow_list_empty(app):
    with app.app_context():
        result = Workflow.query.filter_by(platform="instagram", deleted_at=None).all()
        assert result == []


def test_workflow_create(app):
    with app.app_context():
        wf = Workflow(
            platform="instagram",
            name="Test",
            trigger_keyword="test",
            source_id="https://example.com",
        )
        db.session.add(wf)
        db.session.commit()
        found = Workflow.query.filter_by(name="Test").first()
        assert found is not None
        assert found.platform == "instagram"
