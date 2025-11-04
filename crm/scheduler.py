# crm/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

def start_scheduler():
    scheduler = BackgroundScheduler()

    # Heartbeat: every 5 minutes
    scheduler.add_job(
        'crm.cron.log_crm_heartbeat',
        trigger='interval',
        minutes=5,
        id='crm_heartbeat',
        replace_existing=True,
        coalesce=True
    )

    # Low stock update: every 12 hours
    scheduler.add_job(
        'crm.cron.update_low_stock',
        trigger='interval',
        hours=12,
        id='low_stock_update',
        replace_existing=True,
        coalesce=True
    )

    try:
        scheduler.start()
        logger.info("APScheduler started: heartbeat (5min), low-stock (12h)")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")