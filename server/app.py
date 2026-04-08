from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env import LogisticsEnv
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
def tasks():
    return {"tasks": ["easy", "medium", "hard"]}

@app.post("/reset")
def reset(req: ResetRequest = None):
    task_id = (req.task_id if req else None) or "easy"
    if task_id == "easy":
        orders = easy_task()
    elif task_id == "medium":
        orders = medium_task()
    else:
        orders = hard_task()
    obs = env.reset(orders=orders)
    return {
        "orders": [o.dict() for o in obs.orders],
        "step": obs.step,
        "done": False,
        "feedback": ""
    }

@app.post("/step")
def step(req: StepRequest):
    obs, reward, done, info = env.step(req)
    return {
        "observation": {
            "orders": [o.dict() for o in obs.orders],
            "step": obs.step,
            "done": done,
            "feedback": info.get("feedback", "")
        },
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state():
    obs = env._get_observation()
    return {
        "orders": [o.dict() for o in obs.orders],
        "step": obs.step,
        "done": False
    }
