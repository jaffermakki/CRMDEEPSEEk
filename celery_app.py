from celery.schedules import crontab

# Update the beat_schedule in celery_app.py
app.conf.beat_schedule = {
    "check-warranties-daily": {
        "task": "modules.automation.tasks.task_check_warranty_expiry",
        "schedule": crontab(hour=8, minute=0),  # Runs every day at 8 AM
    },
    "generate-reorder-pos-daily": {
        "task": "modules.automation.tasks.task_generate_reorder_pos",
        "schedule": crontab(hour=9, minute=0), # Runs every day at 9 AM
    },
    "send-daily-digest": {
        "task": "modules.automation.tasks.task_send_daily_digest",
        "schedule": crontab(hour=21, minute=0), # Runs every day at 9 PM
    },
}
