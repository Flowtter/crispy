import asyncio
import math
import time

SLEEP_TIME = 0.3


async def ok():
    await asyncio.sleep(SLEEP_TIME)
    return True


async def ko():
    raise Exception("KO")


async def test_schedule(job_scheduler):
    burst_size = 3
    jobs_length = 8

    job_scheduler.burst_size = burst_size

    ids = []
    for _ in range(jobs_length):
        ids.append(job_scheduler.schedule(ok))

    for _id in ids:
        job = await job_scheduler.find_job(_id)
        assert type(job) != asyncio.Task

    initial_time = time.time()

    await job_scheduler.run()

    duration = time.time() - initial_time
    expected_duration = SLEEP_TIME * math.ceil(jobs_length / burst_size)

    assert expected_duration - 0.2 < duration < expected_duration + 0.2

    for _id in ids:
        job = await job_scheduler.find_job(_id)
        assert type(job) == asyncio.Task
        assert job.done()
        assert job.result() is True


async def test_schedule_ko(job_scheduler):
    job_scheduler.schedule(ko)

    await job_scheduler.run()
