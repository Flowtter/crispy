import asyncio
from datetime import datetime
from typing import Any, Callable, Tuple, Union


class JobScheduler:
    def __init__(self, burst_size: int = 4):
        self._jobs: dict[int, Union[asyncio.Task, Callable]] = {}
        self._running_jobs: list[asyncio.Task] = []

        self.burst_size = burst_size

        self.current_job_id = int(datetime.now().timestamp())

    def schedule(self, job: Callable) -> int:
        _id = self.current_job_id
        self._jobs[_id] = job
        self.current_job_id += 1
        return _id

    async def find_job(self, id: int) -> Union[asyncio.Task, Callable]:
        return self._jobs[id]

    async def run(self) -> None:
        self._running_jobs = []
        await self.__fill_running_jobs()

        while self._running_jobs:
            await asyncio.wait(self._running_jobs, return_when=asyncio.FIRST_COMPLETED)
            for task in self._running_jobs:
                if task.done():
                    if task.exception():
                        pass
                    else:
                        pass
                    self._running_jobs.remove(task)
                    break
            await self.__fill_running_jobs()

    async def __find_next_job(self) -> Tuple[Any, int]:
        for _id, job in self._jobs.items():
            if type(job) != asyncio.Task:
                return job, _id
        return None, -1

    async def __fill_running_jobs(self) -> None:
        while len(self._running_jobs) < self.burst_size:
            job, _id = await self.__find_next_job()
            if job:
                task = asyncio.create_task(job())
                self._running_jobs.append(task)
                self._jobs[_id] = task
            else:
                return
