from datetime import datetime, timezone
from flask import request, jsonify
from flask_login import login_required
from app.workflows import bp
from app.workflows.models import Workflow, WorkflowStep
from app.extensions import db
from app.helpers import not_found, bad_request
from app.messages import AppMessages


@bp.route("", methods=["GET"])
@login_required
def list_workflows():
    platform = request.args.get("platform", "instagram")
    workflows = (Workflow.query
                 .filter_by(platform=platform, deleted_at=None)
                 .order_by(Workflow.priority.desc())
                 .all())
    return jsonify({"workflows": [w.to_dict() for w in workflows], "platform": platform}), 200


@bp.route("", methods=["POST"])
@login_required
def create_workflow():
    data = request.json or {}
    platform = data.get("platform", "instagram")
    if not data.get("name") or not data.get("trigger_keyword") or not data.get("source_id"):
        return bad_request("name, trigger_keyword, and source_id are required")

    wf = Workflow(
        platform=platform,
        name=data["name"],
        trigger_keyword=data["trigger_keyword"],
        source_id=data["source_id"],
        priority=data.get("priority", 1),
        active=data.get("active", True),
        match_mode=data.get("match_mode", "contains"),
        link=data.get("link"),
    )
    db.session.add(wf)

    for i, step_data in enumerate(data.get("steps", [])):
        step = WorkflowStep(
            workflow_id=wf.id,
            step_order=step_data.get("step_order", i),
            step_type=step_data["step_type"],
            message_template=step_data.get("message_template"),
            send_if=step_data.get("send_if"),
            delay_seconds=step_data.get("delay_seconds"),
        )
        wf.steps.append(step)

    db.session.commit()
    return jsonify({"id": wf.id, "platform": platform}), 201


@bp.route("/<workflow_id>", methods=["PUT"])
@login_required
def update_workflow(workflow_id):
    platform = request.args.get("platform", "instagram")
    wf = Workflow.query.filter_by(id=workflow_id, platform=platform, deleted_at=None).first()
    if not wf:
        return not_found(AppMessages.WORKFLOW_NOT_FOUND)

    data = request.json or {}
    wf.name = data.get("name", wf.name)
    wf.trigger_keyword = data.get("trigger_keyword", wf.trigger_keyword)
    wf.source_id = data.get("source_id", wf.source_id)
    wf.priority = data.get("priority", wf.priority)
    wf.active = data.get("active", wf.active)
    wf.match_mode = data.get("match_mode", wf.match_mode)
    wf.link = data.get("link", wf.link)
    wf.updated_at = datetime.now(timezone.utc)

    if "steps" in data:
        for s in wf.steps:
            db.session.delete(s)
        for i, step_data in enumerate(data["steps"]):
            step = WorkflowStep(
                workflow_id=wf.id,
                step_order=step_data.get("step_order", i),
                step_type=step_data["step_type"],
                message_template=step_data.get("message_template"),
                send_if=step_data.get("send_if"),
                delay_seconds=step_data.get("delay_seconds"),
            )
            wf.steps.append(step)

    db.session.commit()
    return jsonify({"id": wf.id, "updated": True}), 200


@bp.route("/<workflow_id>", methods=["DELETE"])
@login_required
def delete_workflow(workflow_id):
    platform = request.args.get("platform", "instagram")
    wf = Workflow.query.filter_by(id=workflow_id, platform=platform, deleted_at=None).first()
    if not wf:
        return not_found(AppMessages.WORKFLOW_NOT_FOUND)
    wf.deleted_at = datetime.now(timezone.utc)
    wf.deleted_by = "admin"
    db.session.commit()
    return jsonify({"deleted": True}), 200


@bp.route("/<workflow_id>/toggle", methods=["POST"])
@login_required
def toggle_workflow(workflow_id):
    platform = request.args.get("platform", "instagram")
    wf = Workflow.query.filter_by(id=workflow_id, platform=platform, deleted_at=None).first()
    if not wf:
        return not_found(AppMessages.WORKFLOW_NOT_FOUND)
    wf.active = not wf.active
    wf.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"id": wf.id, "active": wf.active}), 200
