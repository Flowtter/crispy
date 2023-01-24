import asyncio
import math
import time

import pytest

SLEEP_TIME = 0.3


async def ok():
    await asyncio.sleep(SLEEP_TIME)
    return True


async def ko():
    raise Exception("KO")


async def ok_with_args(a, b):
    await asyncio.sleep(SLEEP_TIME)
    return a + b


async def test_schedule(job_scheduler):
    burst_size = 3
    jobs_length = 8

    job_scheduler.burst_size = burst_size

    ids = []
    for _ in range(jobs_length):
        ids.append(job_scheduler.schedule(ok))

    for _id in ids:
        job = job_scheduler.find_job(_id)
        assert type(job["task"]) != asyncio.Task

    initial_time = time.time()

    await job_scheduler.run()

    duration = time.time() - initial_time
    expected_duration = SLEEP_TIME * math.ceil(jobs_length / burst_size)

    assert expected_duration - 0.2 < duration < expected_duration + 0.2

    for _id in ids:
        job = job_scheduler.find_job(_id)
        assert job["status"] == "completed"

        task = job["task"]
        assert type(task) == asyncio.Task
        assert task.done()
        assert task.result() is True


async def test_schedule_with_args(job_scheduler):
    _id = job_scheduler.schedule(ok_with_args, kwargs={"a": 2, "b": 7})

    await job_scheduler.run()

    job = job_scheduler.find_job(_id)
    assert job["status"] == "completed"

    task = job["task"]
    assert type(task) == asyncio.Task
    assert task.done()
    assert task.result() == 9


async def test_schedule_ko(job_scheduler):
    _id = job_scheduler.schedule(ko)

    await job_scheduler.run()

    job = job_scheduler.find_job(_id)
    assert job["status"] == "failed"

    with pytest.raises(Exception):
        job["task"].result()


async def sleep_test(index):
    await asyncio.sleep(index * 1)


async def test_job_scheduler_time(job_scheduler):
    """
    This test create 5 jobs with a sleep time of 5, 4, 3, 2, 1 seconds.
    The job scheduler burst size is 3, so the first 3 jobs will be executed

    - The first job to finish will be the one with a sleep time of 3 seconds.
    It will then take the 2 second job

    - The second job to finish will be the one with a sleep time of 4 seconds.
    It will then take the 1 second job

    - Then all the jobs should stop at the same time
    """
    job_scheduler.burst_size = 3
    for i in range(5):
        job_scheduler.schedule(sleep_test, kwargs={"index": 5 - i})

    initial_time = time.time()
    job_scheduler.run_in_thread().join()
    duration = time.time() - initial_time

    assert 4.8 < duration < 5.2
