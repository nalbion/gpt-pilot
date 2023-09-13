from fastapi import APIRouter, Depends, HTTPException
from typing import List
from fastapi.responses import StreamingResponse
# from sse_starlette.sse import EventSourceResponse
from agent_protocol import Agent, Step, Task


# async def plan(step: Step) -> Step:
#     task = await Agent.db.get_task(step.task_id)
#     steps = generete_steps(task.input)
#
#     last_step = steps[-1]
#     for step in steps[:-1]:
#        await Agent.db.create_step(task_id=task.task_id, name=step, ...)
#
#     await Agent.db.create_step(task_id=task.task_id, name=last_step, is_last=True)
#     step.output = steps
#     return step
#
#
# async def execute(step: Step) -> Step:
#     # Use tools, websearch, etc.
#     return step

# def get_workspace(task_id: str) -> str:
#     pass
#
#
# Agent.get_workspace = get_workspace


router = APIRouter()

# This just returns the list of task IDs
# @router.get("/agent/tasks", response_model=List[str], tags=["agent"])
# async def list_agent_tasks_ids(filter: str = None) -> List[str]:
#     tasks = [task.task_id for task in await Agent.db.list_tasks()]
#     if filter:
#         tasks = [task for task in tasks if filter in task]
#     return tasks

# Server Sent Events endpoint to listen for DevelopmentSteps
# @router.get("/agent/tasks/{task_id}/steps/stream", response_class=EventSourceResponse, tags=["agent"])
# async def get_step_stream(task_id: str, task_type: str = None):
#     def event_generator():
#         count = 0
#         while True:
#             time.sleep(1)
#             count += 1
#             yield f"data: Event {count}\n\n"
#     return StreamingResponse(event_generator(), media_type="text/event-stream")


async def task_handler(task: Task) -> None:
    """
    POST /agent/tasks calls Agent.db.create_task(input, additional_input)
                      and then calls task_handler(task)
    By default, uses InMemoryTaskDB which sets task_id to uuid.uuid4() & adds task to self._tasks

    :param task:
    :return:
    """

    print('task_handler', task)
    await Agent.db.create_step(task_id=task.task_id, name="plan")
    pass


async def step_handler(step: Step) -> Step:
    print('step_handler', step)
    # if step.name == "plan":
    #     await plan(step)
    # else:
    #     await execute(step)

    return step


def start_server(port: int = 8000):
    print('Starting server...')
    Agent.setup_agent(task_handler, step_handler).start(port, router)


if __name__ == '__main__':
    start_server()
