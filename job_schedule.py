from flask_apscheduler import APScheduler
from automations import get_automation_steps
from automation_runner import run_automation_steps
from downloader import download_file

CRON_SCHEDULES = {
    "hourly": {"hour": "*/1"},
    "threeaday": {"hour": "8,12,16"},
    "daily": {"day": "*/1", "day_of_week": "0-4"},
    "custom": {"day": "*/1", "hour": None, "minute": None, "day_of_week": "0-4"}
}

def add_automation_schedule(scheduler: APScheduler, automation_id: str, cron: dict, automation_type: str) -> None:
    """Create a job for the automation with the given ID and
    schedule it to run on the given cron schedule."""
    replace = True if scheduler.get_job(automation_id) else False
    if (automation_type == 0):
        automation_steps = get_automation_steps(automation_id)
        automation_steps = [dict(row) for row in automation_steps]
        scheduler.add_job(id=automation_id, func=run_automation_steps, replace_existing=replace, kwargs={"automation_id": automation_id, "steps": automation_steps}, trigger='cron', **cron)
    else:
        scheduler.add_job(id=automation_id, func=download_file, replace_existing=replace, kwargs={"automation_id": automation_id}, trigger='cron', **cron)

def remove_automation_schedule(scheduler: APScheduler, automation_id: str) -> None:
    """Remove any jobs which have an ID the same as the given
    automation ID."""
    scheduler.remove_job(automation_id)

def pause_automation_schedule(scheduler: APScheduler, automation_id: str) -> None:
    """Pause the scheduled job with the given ID."""
    scheduler.pause_job(automation_id)

def resume_automation_schedule(scheduler: APScheduler, automation_id: str) -> None:
    """Resume the scheduled job with the given ID."""
    scheduler.resume_job(automation_id)

def get_automation_next_run_time(scheduler: APScheduler, automation_id: str) -> str|None:
    job = scheduler.get_job(automation_id)
    if job:
        return job.next_run_time
    return None