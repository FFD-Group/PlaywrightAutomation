from __future__ import annotations

from typing import Any, Dict, Optional

from automations import get_scheduled_automations
from job_schedule import add_automation_schedule, remove_automation_schedule, CRON_SCHEDULES

_app = None
_scheduler = None


def init_scheduler_sync(app, scheduler) -> None:
    """
    Called once at startup (in scheduler service) to provide globals.
    We DO NOT pass app/scheduler into scheduled jobs (not picklable).
    """
    global _app, _scheduler
    _app = app
    _scheduler = scheduler


def _build_cron(schedule: str, schedule_time: str | None) -> dict | None:
    if schedule not in CRON_SCHEDULES:
        return None

    cron = dict(CRON_SCHEDULES[schedule])

    if schedule == "custom":
        if not schedule_time or ":" not in schedule_time:
            return None
        hh, mm = schedule_time.split(":")
        cron["hour"] = str(int(hh))
        cron["minute"] = str(int(mm))

    return cron


def sync_schedules_job() -> None:
    """
    This is the function APScheduler runs.
    Must be top-level and take no args (so it's picklable).
    """
    if _app is None or _scheduler is None:
        return

    with _app.app_context():
        rows = get_scheduled_automations()

        desired: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            automation_id = str(row["id"])
            schedule = row["schedule"]
            schedule_time = row.get("schedule_time")
            automation_type = row["type"]

            cron = _build_cron(schedule, schedule_time)
            if not cron:
                continue

            desired[automation_id] = {"cron": cron, "type": automation_type}

        # Add/update desired jobs
        for automation_id, meta in desired.items():
            add_automation_schedule(
                scheduler=_scheduler,
                automation_id=automation_id,
                cron=meta["cron"],
                automation_type=meta["type"],
            )

        # Remove stale numeric-id jobs
        for job in _scheduler.get_jobs():
            job_id = str(job.id)
            if job_id.isdigit() and job_id not in desired:
                remove_automation_schedule(_scheduler, job_id)
                
        _app.logger.info(f"Sync: desired job ids = {list(desired.keys())}")
