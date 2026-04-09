from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os
import uvicorn

from env import LogisticsEnv, Action, ActionType
from tasks import easy_task, medium_task, hard_task, grade_easy, grade_medium, grade_hard

app = FastAPI()

GRADERS = {"easy": grade_easy, "medium": grade_medium, "hard": grade_hard}

current_task_id = "easy"
current_all_orders = []
env = LogisticsEnv()

class ResetRequest(BaseModel):
    task_id: Optional[str] = "easy"

class StepRequest(BaseModel):
    order_id: int
    reasoning: Optional[str] = ""

@app.get("/")
def root():
    return {"status": "ok", "service": "logistics_flow"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return {"tasks": ["easy", "medium", "hard"]}

@app.post("/reset")
def reset(req: ResetRequest = None):
    global current_task_id, current_all_orders, env
    current_task_id = (req.task_id if req and req.task_id else "easy")
    if current_task_id not in GRADERS:
        current_task_id = "easy"
    if current_task_id == "easy":
        current_all_orders = easy_task()
    elif current_task_id == "medium":
        current_all_orders = medium_task()
    else:
        current_all_orders = hard_task()
    env = LogisticsEnv()
    obs = env.reset(orders=list(current_all_orders))
    reward = GRADERS[current_task_id](env)
    return {
        "observation": {
            "orders": [o.dict() for o in obs.orders],
            "step": obs.current_step,
            "done": False,
            "feedback": f"Task {current_task_id} started"
        },
        "reward": reward,
        "done": False,
        "info": {}
    }

@app.post("/step")
def step(req: StepRequest):
    action = Action(action_type=ActionType.FULFILL, order_id=req.order_id)
    obs, _, done_env, info = env.step(action)
    done = done_env or len(obs.orders) == 0
    reward = GRADERS[current_task_id](env)
    return {
        "observation": {
            "orders": [o.dict() for o in obs.orders],
            "step": obs.current_step,
            "done": done,
            "feedback": info.get("error", "ok") if isinstance(info, dict) else "ok"
        },
        "reward": reward,
        "done": done,
        "info": {}
    }

@app.get("/state")
def state():
    obs = env._get_observation()
    return {
        "observation": {
            "orders": [o.dict() for o in obs.orders],
            "step": obs.current_step,
            "done": False,
            "feedback": ""
        },
        "reward": GRADERS[current_task_id](env),
        "done": False,
        "info": {}
    }

def main():
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
