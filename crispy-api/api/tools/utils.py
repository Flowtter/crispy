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


def levenstein_distance(s1: str, s2: str) -> int:
    """Calculates the levenstein distance between two strings"""
    if len(s1) < len(s2):
        return levenstein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))

    for i, c1 in enumerate(s1):
        current_row = [i + 1]

        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))

        previous_row = current_row

    return previous_row[-1]
