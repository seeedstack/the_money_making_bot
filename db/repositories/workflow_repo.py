from sqlalchemy import text
from core.models.workflow import Workflow, WorkflowStep, StepType, SendIf

class WorkflowRepository:
    """Query workflows by platform."""

    def __init__(self, db_engine):
        self.engine = db_engine

    def get_all(self, platform: str) -> list:
        """Get all active workflows for platform."""
        with self.engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT id, platform, name, trigger_keyword, source_id, priority, active, match_mode, link "
                "FROM workflows WHERE platform = :platform AND active = 1 "
                "ORDER BY priority DESC"
            ), {"platform": platform}).fetchall()

            result = []
            for row in rows:
                steps = self._get_steps(conn, row[0])
                result.append(Workflow(
                    id=row[0],
                    name=row[2],
                    platform=row[1],
                    trigger_keyword=row[3],
                    source_id=row[4],
                    priority=row[5],
                    active=bool(row[6]),
                    match_mode=row[7],
                    link=row[8],
                    steps=steps
                ))
            return result

    def get_by_id(self, platform: str, workflow_id: int):
        """Get workflow by ID."""
        with self.engine.connect() as conn:
            row = conn.execute(text(
                "SELECT id, platform, name, trigger_keyword, source_id, priority, active, match_mode, link "
                "FROM workflows WHERE id = :id AND platform = :platform"
            ), {"id": workflow_id, "platform": platform}).fetchone()

            if not row:
                return None

            steps = self._get_steps(conn, row[0])
            return Workflow(
                id=row[0],
                name=row[2],
                platform=row[1],
                trigger_keyword=row[3],
                source_id=row[4],
                priority=row[5],
                active=bool(row[6]),
                match_mode=row[7],
                link=row[8],
                steps=steps
            )

    def insert(self, platform: str, workflow_data: dict):
        """Insert workflow and return ID."""
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "INSERT INTO workflows "
                "(platform, name, trigger_keyword, source_id, priority, active, match_mode, link) "
                "VALUES (:platform, :name, :trigger_keyword, :source_id, :priority, :active, :match_mode, :link)"
            ), {
                "platform": platform,
                "name": workflow_data["name"],
                "trigger_keyword": workflow_data["trigger_keyword"],
                "source_id": workflow_data["source_id"],
                "priority": workflow_data.get("priority", 1),
                "active": workflow_data.get("active", True),
                "match_mode": workflow_data.get("match_mode", "contains"),
                "link": workflow_data.get("link")
            })

            workflow_id = result.lastrowid

            if "steps" in workflow_data:
                for step_data in workflow_data["steps"]:
                    conn.execute(text(
                        "INSERT INTO workflow_steps "
                        "(workflow_id, step_order, step_type, message_template, send_if, delay_seconds) "
                        "VALUES (:workflow_id, :step_order, :step_type, :message_template, :send_if, :delay_seconds)"
                    ), {
                        "workflow_id": workflow_id,
                        "step_order": step_data["step_order"],
                        "step_type": step_data["step_type"],
                        "message_template": step_data.get("message_template"),
                        "send_if": step_data.get("send_if"),
                        "delay_seconds": step_data.get("delay_seconds")
                    })

            conn.commit()
            return workflow_id

    def update(self, platform: str, workflow_id: int, workflow_data: dict):
        """Update workflow."""
        with self.engine.connect() as conn:
            conn.execute(text(
                "UPDATE workflows SET name = :name, trigger_keyword = :trigger_keyword, "
                "source_id = :source_id, priority = :priority, active = :active, "
                "match_mode = :match_mode, link = :link, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = :id AND platform = :platform"
            ), {
                "id": workflow_id,
                "platform": platform,
                "name": workflow_data.get("name"),
                "trigger_keyword": workflow_data.get("trigger_keyword"),
                "source_id": workflow_data.get("source_id"),
                "priority": workflow_data.get("priority"),
                "active": workflow_data.get("active"),
                "match_mode": workflow_data.get("match_mode"),
                "link": workflow_data.get("link")
            })
            conn.commit()

    def delete(self, platform: str, workflow_id: int):
        """Soft-delete workflow."""
        with self.engine.connect() as conn:
            conn.execute(text(
                "UPDATE workflows SET active = 0, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = :id AND platform = :platform"
            ), {"id": workflow_id, "platform": platform})
            conn.commit()

    def _get_steps(self, conn, workflow_id: int) -> list:
        """Fetch all steps for a workflow."""
        rows = conn.execute(text(
            "SELECT step_order, step_type, message_template, send_if, delay_seconds "
            "FROM workflow_steps WHERE workflow_id = :workflow_id ORDER BY step_order"
        ), {"workflow_id": workflow_id}).fetchall()

        return [
            WorkflowStep(
                step_order=row[0],
                step_type=StepType(row[1]),
                message_template=row[2],
                send_if=SendIf(row[3]) if row[3] else None,
                delay_seconds=row[4]
            )
            for row in rows
        ]
