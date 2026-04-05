import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from env import LogisticsEnv, Action

# -------------------------
# LOAD ENV
# -------------------------
load_dotenv()

# -------------------------
# ENV CONFIG (MANDATORY)
# -------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY if OPENAI_API_KEY else "dummy",
    base_url=API_BASE_URL
)

# -------------------------
# FALLBACK POLICY
# -------------------------
def get_priority_value(priority):
    return {"high": 3, "medium": 2, "low": 1}.get(priority, 0)

def fallback_action(observation):
    sorted_orders = sorted(
        observation.orders,
        key=lambda x: get_priority_value(x.priority),
        reverse=True
    )

    for order in sorted_orders:
        if observation.inventory.get(order.item, 0) >= order.qty:
            return Action(action_type="fulfill", order_id=order.id)

    # optional restock improvement
    if sorted_orders:
        return Action(action_type="restock", item=sorted_orders[0].item, quantity=2)

    return Action(action_type="wait")

# -------------------------
# MODEL ACTION
# -------------------------
def get_model_action(observation, step):
    # reduce API usage
    if step % 2 != 0:
        return fallback_action(observation)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Return action in JSON with action_type, order_id, item, quantity."},
                {"role": "user", "content": str(observation)}
            ],
            response_format={"type": "json_object"}
        )

        action_dict = json.loads(response.choices[0].message.content)
        return Action(**action_dict)

    except Exception:
        return fallback_action(observation)

# -------------------------
# RUN TASK
# -------------------------
def run_task(task_name, task_fn):
    print(f"[START] {task_name.upper()}")

    env = LogisticsEnv()
    obs = env.reset(orders=task_fn())

    for step in range(10):
        print(f"[STEP {step}]")

        action = get_model_action(obs, step)
        obs, reward, done, _ = env.step(action)

        print(f"Action: {action.action_type}")
        print(f"Reward: {reward}")

        if done:
            break

    print(f"[END] {task_name.upper()}")

# -------------------------
# MAIN
# -------------------------
def main():
    from tasks import easy_task, medium_task, hard_task

    run_task("easy", easy_task)
    run_task("medium", medium_task)
    run_task("hard", hard_task)

# -------------------------
# ENTRY
# -------------------------
if __name__ == "__main__":
    main()