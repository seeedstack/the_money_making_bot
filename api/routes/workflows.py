from flask import Blueprint, request, jsonify
from db.database import Database
from db.repositories.workflow_repo import WorkflowRepository

bp = Blueprint("workflows", __name__, url_prefix="/api/workflows")

def get_repo():
    db = Database()
    return WorkflowRepository(db.engine)

@bp.route("", methods=["GET"])
def get_workflows():
    """Get workflows for platform."""
    platform = request.args.get("platform", "instagram")
    repo = get_repo()
    workflows = repo.get_all(platform)
    return jsonify({
        "workflows": [
            {
                "id": wf.id,
                "name": wf.name,
                "platform": wf.platform,
                "trigger_keyword": wf.trigger_keyword,
                "source_id": wf.source_id,
                "priority": wf.priority,
                "active": wf.active,
                "match_mode": wf.match_mode,
                "link": wf.link,
                "steps": [
                    {
                        "step_order": s.step_order,
                        "step_type": s.step_type.value,
                        "message_template": s.message_template,
                        "send_if": s.send_if.value if s.send_if else None,
                        "delay_seconds": s.delay_seconds
                    }
                    for s in wf.steps
                ]
            }
            for wf in workflows
        ],
        "platform": platform
    }), 200

@bp.route("", methods=["POST"])
def create_workflow():
    """Create workflow."""
    data = request.json
    platform = data.get("platform", "instagram")
    repo = get_repo()
    wf_id = repo.insert(platform, data)
    return jsonify({"id": wf_id, "platform": platform}), 201

@bp.route("/<int:workflow_id>", methods=["PUT"])
def update_workflow(workflow_id):
    """Update workflow."""
    data = request.json
    platform = data.get("platform", "instagram")
    repo = get_repo()
    repo.update(platform, workflow_id, data)
    return jsonify({"id": workflow_id, "updated": True}), 200

@bp.route("/<int:workflow_id>", methods=["DELETE"])
def delete_workflow(workflow_id):
    """Soft-delete workflow."""
    platform = request.args.get("platform", "instagram")
    repo = get_repo()
    repo.delete(platform, workflow_id)
    return jsonify({"deleted": True}), 200

@bp.route("/<int:workflow_id>/toggle", methods=["POST"])
def toggle_workflow(workflow_id):
    """Toggle workflow active status."""
    platform = request.args.get("platform", "instagram")
    repo = get_repo()
    wf = repo.get_by_id(platform, workflow_id)
    if wf:
        repo.update(platform, workflow_id, {"active": not wf.active})
    return jsonify({"id": workflow_id, "toggled": True}), 200
