"""Background job scheduler for feed processing."""

from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.src.infrastructure.database import SessionLocal
from backend.src.infrastructure.feed_parser import FeedParserService
from backend.src.infrastructure.settings_store import load_settings
from backend.src.infrastructure.unit_of_work import UnitOfWork
from shared.logging import get_logger

logger = get_logger(__name__)


class FeedScheduler:
    """Background job scheduler for feed polling, cleanup, and health checks."""

    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler()
        self._logger = get_logger(__name__)

    def start(self) -> None:
        """Start the scheduler with all configured jobs."""
        self._scheduler.add_job(
            self._poll_all_feeds,
            trigger=IntervalTrigger(minutes=15),
            id="poll_feeds",
            name="Poll all feeds",
        )
        self._scheduler.add_job(
            self._cleanup_old_news,
            trigger=IntervalTrigger(hours=24),
            id="cleanup",
            name="Cleanup old news",
        )
        self._scheduler.add_job(
            self._health_check_sources,
            trigger=IntervalTrigger(hours=6),
            id="health_check",
            name="Health check sources",
        )
        self._scheduler.start()
        self._logger.info("Scheduler started with 3 jobs")

    def shutdown(self) -> None:
        """Shutdown the scheduler gracefully."""
        self._scheduler.shutdown(wait=True)
        self._logger.info("Scheduler shut down")

    def trigger_poll_now(self) -> None:
        """Trigger an immediate poll of all feeds."""
        job = self._scheduler.get_job("poll_feeds")
        if job:
            job.modify(next_run_time=datetime.now())
            self._logger.info("Manual feed poll triggered")

    def get_status(self) -> dict[str, object]:
        """Return current scheduler status and job information."""
        jobs: list[dict[str, str | None]] = []
        for job in self._scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
            })
        return {
            "running": self._scheduler.running,
            "jobs": jobs,
        }

    def _poll_all_feeds(self) -> None:
        """Poll all feeds with active subscriptions that are due for an update."""
        db = SessionLocal()
        try:
            uow = UnitOfWork(db)
            subscribed_ids = uow.subscription_repository.get_subscribed_source_ids(user_id=1)
            if not subscribed_ids:
                return
            sources = [
                s for s in uow.source_repository.get_all()
                if s.id in set(subscribed_ids)
            ]
            for source in sources:
                if source.last_fetched is not None:
                    elapsed = (datetime.now(UTC) - source.last_fetched).total_seconds() / 60
                    if elapsed < source.update_frequency_minutes:
                        continue
                parser = FeedParserService(uow)
                count = parser.parse_and_import(source)
                self._logger.info(
                    "Polled source %s: %d new items", source.name, count
                )
        except Exception:
            self._logger.exception("Error polling feeds")
        finally:
            db.close()

    def _cleanup_old_news(self) -> None:
        """Delete news items older than the configured retention period."""
        db = SessionLocal()
        try:
            uow = UnitOfWork(db)
            settings = load_settings()
            retention_days = settings.get("news_retention_days", 30)
            cutoff = datetime.now(UTC) - timedelta(days=retention_days)
            from backend.src.infrastructure.models import NewsItem

            deleted = db.query(NewsItem).filter(NewsItem.fetched_at < cutoff).delete()
            uow.commit()
            self._logger.info("Cleaned up %d old news items", deleted)
        except Exception:
            self._logger.exception("Error during news cleanup")
            db.rollback()
        finally:
            db.close()

    def _health_check_sources(self) -> None:
        """Run stateful health checks on all subscribed sources."""
        from backend.src.infrastructure.health_monitor import HealthMonitorService

        db = SessionLocal()
        try:
            uow = UnitOfWork(db)
            monitor = HealthMonitorService(uow)
            results = monitor.check_all_subscribed(user_id=1)

            healthy = sum(1 for r in results if r["new_status"] == "healthy")
            degraded = sum(1 for r in results if r["new_status"] != "healthy")
            self._logger.info(
                "Health check complete: %d healthy, %d degraded/unhealthy/dead",
                healthy, degraded,
            )
        except Exception:
            self._logger.exception("Error during health check")
        finally:
            db.close()
