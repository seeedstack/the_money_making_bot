from flask import Blueprint, request, jsonify

bp = Blueprint("workflows", __name__, url_prefix="/api/workflows")

@bp.route("", methods=["GET"])
def get_workflows():
    """Get workflows for platform. Stub: return []"""
    platform = request.args.get("platform", "instagram")
    return jsonify({"workflows": [], "platform": platform}), 200

@bp.route("", methods=["POST"])
def create_workflow():
    """Create workflow. Stub: return new workflow"""
    data = request.json
    return jsonify({"id": 1, "name": data.get("name"), "platform": data.get("platform")}), 201

@bp.route("/<int:workflow_id>", methods=["PUT"])
def update_workflow(workflow_id):
    """Update workflow. Stub: return updated"""
    data = request.json
    return jsonify({"id": workflow_id, "updated": True}), 200

@bp.route("/<int:workflow_id>", methods=["DELETE"])
def delete_workflow(workflow_id):
    """Delete workflow. Stub: return ok"""
    return jsonify({"deleted": True}), 200

@bp.route("/<int:workflow_id>/toggle", methods=["POST"])
def toggle_workflow(workflow_id):
    """Toggle workflow active status. Stub: return ok"""
    return jsonify({"id": workflow_id, "toggled": True}), 200
