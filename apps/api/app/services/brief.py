from datetime import datetime, date, timedelta
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.core import User, Context, Project, Task, Deadline, Decision, ExecutiveBrief

class BriefingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_brief(self, user: User, target_date: Optional[date] = None) -> ExecutiveBrief:
        if target_date is None:
            target_date = datetime.utcnow().date()

        # 1. Gather all active contexts
        ctx_stmt = select(Context).where(Context.user_id == user.id, Context.is_active == True)
        ctx_res = await self.db.execute(ctx_stmt)
        contexts = ctx_res.scalars().all()
        
        # 2. Gather all active projects
        proj_stmt = select(Project).where(Project.user_id == user.id)
        proj_res = await self.db.execute(proj_stmt)
        projects = proj_res.scalars().all()
        
        # 3. Gather open tasks
        task_stmt = select(Task).where(Task.user_id == user.id, Task.status != "completed").order_by(Task.created_at.desc())
        task_res = await self.db.execute(task_stmt)
        tasks = task_res.scalars().all()
        
        # 4. Gather upcoming deadlines
        deadline_stmt = select(Deadline).where(Deadline.user_id == user.id, Deadline.due_at >= datetime.utcnow()).order_by(Deadline.due_at.asc())
        dl_res = await self.db.execute(deadline_stmt)
        deadlines = dl_res.scalars().all()
        
        # 5. Gather recent decisions (created in last 48 hours)
        since_date = datetime.utcnow() - timedelta(hours=48)
        dec_stmt = select(Decision).where(Decision.user_id == user.id, Decision.created_at >= since_date).order_by(Decision.created_at.desc())
        dec_res = await self.db.execute(dec_stmt)
        decisions = dec_res.scalars().all()

        # 6. Build the Structured Brief
        structured = {
            "active_projects": [p.project_name for p in projects],
            "current_contexts": [c.name for c in contexts],
            "top_priorities": [],
            "open_tasks": [t.task for t in tasks],
            "upcoming_deadlines": [f"{d.title} (due {d.due_at.strftime('%Y-%m-%d')})" for d in deadlines],
            "recent_decisions": [d.chosen_option for d in decisions],
            "suggested_next_actions": []
        }

        # Populate top_priorities
        for t in tasks[:2]:
            structured["top_priorities"].append(f"Complete task: {t.task}")
        for d in deadlines[:1]:
            structured["top_priorities"].append(f"Meet deadline: {d.title}")
            
        if not structured["top_priorities"]:
            structured["top_priorities"].append("No immediate priorities. Focus on planning.")

        # Populate suggested next actions
        if tasks:
            structured["suggested_next_actions"].append(f"Begin working on: {tasks[0].task}")
        if deadlines:
            structured["suggested_next_actions"].append(f"Prepare for upcoming deadline: {deadlines[0].title}")
        if projects and not tasks:
            structured["suggested_next_actions"].append(f"Define first actionable tasks for project: {projects[0].project_name}")
            
        if not structured["suggested_next_actions"]:
            structured["suggested_next_actions"].append("Create a new project or start a session to capture work.")

        # 7. Render Brief to Text
        display_name = user.display_name or "Builder"
        lines = [
            f"GOOD MORNING {display_name.upper()}",
            ""
        ]

        if structured["active_projects"]:
            lines.append("Active Project:")
            for p in structured["active_projects"]:
                lines.append(f"- {p}")
            lines.append("")

        if structured["current_contexts"]:
            lines.append("Current Context:")
            for c in structured["current_contexts"]:
                lines.append(f"- {c}")
            lines.append("")

        if structured["open_tasks"]:
            lines.append("Open Tasks:")
            for t in structured["open_tasks"]:
                lines.append(f"- {t}")
            lines.append("")

        if deadlines:
            lines.append("Upcoming Deadlines:")
            for d in deadlines:
                due_str = d.due_at.strftime('%Y-%m-%d %H:%M')
                lines.append(f"- {d.title} (due {due_str})")
            lines.append("")

        if decisions:
            lines.append("Recent Decisions:")
            for d in decisions:
                lines.append(f"- {d.chosen_option}")
            lines.append("")

        if structured["suggested_next_actions"]:
            lines.append("Suggested Next Action:")
            for a in structured["suggested_next_actions"]:
                lines.append(f"- {a}")
            lines.append("")

        rendered = "\n".join(lines).strip()

        brief = ExecutiveBrief(
            user_id=user.id,
            brief_date=target_date,
            structured_brief=structured,
            rendered_brief=rendered
        )
        return brief
