import asyncio
import logging
from threading import Thread
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, no_type_check

from bson import ObjectId

logger = logging.getLogger("uvicorn")


class JobScheduler:
    def __init__(self, burst_size: int = 4):
        self._jobs: Dict[ObjectId, Any] = {}
        self._running_jobs: List[Dict[str, Any]] = []

        self.burst_size = burst_size

    def schedule(self, job: Callable, kwargs: Any = {}) -> ObjectId:
        job_id = ObjectId()
        self._jobs[job_id] = {"task": job, "kwargs": kwargs, "status": "scheduled"}
        return job_id

    def find_job(self, job_id: ObjectId) -> Optional[Any]:
        if job_id not in self._jobs:
            return None
        return self._jobs[job_id]

    async def run(self) -> None:
        self._running_jobs = []
        await self.__fill_running_jobs()

        while self._running_jobs:
            tasks = [job["task"] for job in self._running_jobs]
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for i in range(len(tasks)):
                if tasks[i].done():
                    job_id = self._running_jobs[i]["id"]
                    if tasks[i].exception():
                        self._jobs[job_id] = {
                            **self._jobs[job_id],
                            "status": "failed",
                        }
                        logger.error(f"Job {job_id} failed")
                        logger.debug(tasks[i].exception())
                    else:
                        self._jobs[job_id] = {
                            **self._jobs[job_id],
                            "status": "completed",
                        }
                        logger.debug(f"Job {job_id} completed")
                    self._running_jobs.pop(i)
                    break
            await self.__fill_running_jobs()

    async def __find_next_job(
        self,
    ) -> Tuple[
        Optional[Tuple[Union[asyncio.Task, Callable]]],
        Optional[int],
        Optional[Dict[str, Any]],
    ]:
        for job_id, job in self._jobs.items():
            if job["status"] == "scheduled":
                return job["task"], job_id, job["kwargs"]
        return None, None, None

    @no_type_check
    async def __fill_running_jobs(self) -> None:
        while len(self._running_jobs) < self.burst_size:
            job, job_id, kwargs = await self.__find_next_job()
            if job:
                logger.debug(f"Starting job {job_id} {job.__name__}")
                task = asyncio.create_task(job(**kwargs))
                job_to_add = {"task": task, "id": job_id}
                self._running_jobs.append(job_to_add)

                self._jobs[job_id] = {
                    **self._jobs[job_id],
                    **job_to_add,
                    "status": "running",
                }
            else:
                return

    def run_in_thread(self) -> Thread:
        def __sync_run() -> None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.run_until_complete(self.run())
            loop.close()

        thread = Thread(target=__sync_run)
        thread.start()
        return thread
