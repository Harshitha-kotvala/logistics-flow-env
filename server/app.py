from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import sys
sys.path.insert(0, "/app")

from env import LogisticsEnv, Action, ActionType
from tasks import easy_task, medium_task, hard_task

app = FastAPI()
env = LogisticsEnv()

class ResetRequest(BaseModel):
    task_id: Optional[str] = "easy"

class StepRequest(BaseModel):
    order_id: int
    reasoning: Optional[str] = ""

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return {"tasks": ["easy", "medium", "hard"]}

@app.post("/reset")
def reset(req: ResetRequest = None):
    task_id = "easy"
    if req and req.task_id:
        task_id = req.task_id

    if task_id == "easy":
        orders = easy_task()
    elif task_id == "medium":
        orders = medium_task()
    else:
        orders = hard_task()

    obs = env.reset(orders=orders)

    return {
        "orders": [o.dict() for o in obs.orders],
        "step": obs.current_step,
        "done": False,
        "feedback": ""
    }

@app.post("/step")
def step(req: StepRequest):
    # Convert judge's {order_id} into env's Action format
    action = Action(
        action_type=ActionType.FULFILL,
        order_id=req.order_id
    )
    obs, reward, done, info = env.step(action)

    return {
        "observation": {
            "orders": [o.dict() for o in obs.orders],
            "step": obs.current_step,
            "done": done,
            "feedback": info.get("feedback", info.get("error", "")) if isinstance(info, dict) else ""
        },
        "reward": reward,
        "done": done,
        "info": info if isinstance(info, dict) else {}
    }

@app.get("/state")
def state():
    obs = env._get_observation()
    return {
        "orders": [o.dict() for o in obs.orders],
        "step": obs.current_step,
        "done": False,
        "feedback": ""
    }
