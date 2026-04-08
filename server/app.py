from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import sys
sys.path.insert(0, "/app")

from env import LogisticsEnv, Action, ActionType
from tasks import easy_task, medium_task, hard_task, grade_easy, grade_medium, grade_hard

app = FastAPI()

# One env + grader per task
TASKS = {
    "easy":   (easy_task,   grade_easy),
    "medium": (medium_task, grade_medium),
    "hard":   (hard_task,   grade_hard),
}

# Global state
current_task_id = "easy"
current_all_orders = []
fulfilled_ids = []
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
    return {"tasks": list(TASKS.keys())}

@app.post("/reset")
def reset(req: ResetRequest = None):
    global current_task_id, current_all_orders, fulfilled_ids, env

    current_task_id = (req.task_id if req and req.task_id else "easy")
    if current_task_id not in TASKS:
        current_task_id = "easy"

    task_fn, _ = TASKS[current_task_id]
    current_all_orders = task_fn()
    fulfilled_ids = []
    env = LogisticsEnv()
    obs = env.reset(orders=list(current_all_orders))

    return {
        "orders": [o.dict() for o in obs.orders],
        "step": obs.current_step,
        "done": False,
        "feedback": f"Task {current_task_id} started"
    }

@app.post("/step")
def step(req: StepRequest):
    global fulfilled_ids

    action = Action(action_type=ActionType.FULFILL, order_id=req.order_id)
    obs, _, done, info = env.step(action)

    # Track fulfilled order
    if req.order_id not in fulfilled_ids:
        # Check if it was actually fulfilled (no longer in obs.orders)
        remaining_ids = [o.id for o in obs.orders]
        if req.order_id not in remaining_ids:
            fulfilled_ids.append(req.order_id)

    # Grade using task grader
    _, grade_fn = TASKS[current_task_id]
    reward = grade_fn(fulfilled_ids, current_all_orders)

    done = len(obs.orders) == 0

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
        "orders": [o.dict() for o in obs.orders],
        "step": obs.current_step,
        "done": False,
        "feedback": ""
    }

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
