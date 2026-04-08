from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import sys
sys.path.insert(0, "/app")

from env import LogisticsEnv, Action, ActionType
from tasks import easy_task, medium_task, hard_task

app = FastAPI()

WEIGHTS = {"low": 1, "medium": 2, "high": 3}

current_task_id = "easy"
current_all_orders = []
fulfilled_ids = []
env = LogisticsEnv()

class ResetRequest(BaseModel):
    task_id: Optional[str] = "easy"

class StepRequest(BaseModel):
    order_id: int
    reasoning: Optional[str] = ""

def compute_reward(task_id, fulfilled_ids, all_orders):
    if not all_orders:
        return 0.5
    if task_id == "easy":
        total = len(all_orders)
        done = len(fulfilled_ids)
        raw = done / total
    else:
        total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
        done_w  = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id in fulfilled_ids)
        raw = done_w / total_w if total_w > 0 else 0
    # STRICTLY between 0 and 1 — never 0.0 or 1.0
    return round(max(0.01, min(0.99, raw + 0.001)), 6)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return {"tasks": ["easy", "medium", "hard"]}

@app.post("/reset")
def reset(req: ResetRequest = None):
    global current_task_id, current_all_orders, fulfilled_ids, env

    current_task_id = (req.task_id if req and req.task_id else "easy")
    if current_task_id not in ["easy", "medium", "hard"]:
        current_task_id = "easy"

    if current_task_id == "easy":
        current_all_orders = easy_task()
    elif current_task_id == "medium":
        current_all_orders = medium_task()
    else:
        current_all_orders = hard_task()

    fulfilled_ids = []
    env = LogisticsEnv()
    obs = env.reset(orders=list(current_all_orders))

    return {
        "orders": [o.dict() for o in obs.orders],
        "step": obs.current_step,
        "done": False,
        "feedback": f"Task {current_task_id} started with {len(current_all_orders)} orders"
    }

@app.post("/step")
def step(req: StepRequest):
    global fulfilled_ids

    action = Action(action_type=ActionType.FULFILL, order_id=req.order_id)
    obs, _, done, info = env.step(action)

    # Track fulfilled orders
    remaining_ids = [o.id for o in obs.orders]
    if req.order_id not in remaining_ids and req.order_id not in fulfilled_ids:
        fulfilled_ids.append(req.order_id)

    done = len(obs.orders) == 0
    reward = compute_reward(current_task_id, fulfilled_ids, current_all_orders)

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
    _, grade_reward = compute_reward(current_task_id, fulfilled_ids, current_all_orders), None
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
