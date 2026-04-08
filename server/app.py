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

def safe_reward(raw):
    return round(min(0.99, max(0.01, float(raw))), 6)

def compute_score():
    if not current_all_orders:
        return 0.5
    if current_task_id == "easy":
        total = len(current_all_orders)
        done  = len(fulfilled_ids)
        return safe_reward(done / total)
    else:
        total_w = sum(WEIGHTS.get(o.priority, 1) for o in current_all_orders)
        done_w  = sum(WEIGHTS.get(o.priority, 1) for o in current_all_orders if o.id in fulfilled_ids)
        return safe_reward(done_w / total_w if total_w > 0 else 0)

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
        "feedback": f"Task {current_task_id} started",
        "reward": 0.5
    }

@app.post("/step")
def step(req: StepRequest):
    global fulfilled_ids

    action = Action(action_type=ActionType.FULFILL, order_id=req.order_id)
    obs, _, done_env, info = env.step(action)

    remaining_ids = [o.id for o in obs.orders]
    if req.order_id not in remaining_ids and req.order_id not in fulfilled_ids:
        fulfilled_ids.append(req.order_id)

    done = len(obs.orders) == 0
    reward = compute_score()

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
        "feedback": "",
        "reward": compute_score()
    }

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
