"""ApplyFlow background scheduler.

Runs the pipeline every N minutes.
Intended for local / always-on execution.
On Render, run via a separate worker or cron.
"""
import sys, time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r"C:\va-pipeline")
sys.path.insert(0, str(ROOT))

from pipeline_runner import run_pipeline
from governance import log_event


def main():
    interval_minutes = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print(f"Scheduler started: pipeline every {interval_minutes} minutes")
    log_event("scheduler_start", {"interval_minutes": interval_minutes})
    while True:
        try:
            print(f"\n[{datetime.now(timezone.utc).isoformat()}] Running pipeline")
            failed = run_pipeline()
            if failed:
                print("Failed steps:", failed)
            else:
                print("Pipeline OK")
            log_event(
                "scheduler_sleep",
                {"next_run_minutes": interval_minutes},
            )
        except KeyboardInterrupt:
            log_event("scheduler_stop", {"reason": "keyboard"})
            break
        except Exception as e:
            log_event("scheduler_error", {"error": str(e)})
        time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    main()
