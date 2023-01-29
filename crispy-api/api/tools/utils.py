from typing import Any, Dict, List

from api.models.highlight import Highlight
from api.tools.job_scheduler import JobScheduler


def get_all_jobs_from_highlights(
    job_scheduler: JobScheduler, highlights: List[Highlight]
) -> List[Dict]:
    jobs = []
    for highlight in highlights:
        result = {
            "_id": str(highlight.id),
            "index": highlight.index,
            "status": "completed",
            "name": highlight.name,
        }
        if highlight.job_id is not None:
            job = job_scheduler.find_job(highlight.job_id)
            result["status"] = job["status"] if job is not None else "completed"
        jobs.append(result)
    return jobs


def sanitize_dict(d: Any) -> Dict:
    """Remove all keys with None, False or Empty string values from a dict/object""" ""
    return {k: v for k, v in d.items() if v}
