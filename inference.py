import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from env import LogisticsEnv, Action

load_dotenv()

# -------------------------
# REQUIRED ENV VARIABLES (from judge)
# -------------------------
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.getenv("API_KEY")

# Initialize OpenAI client 
client = OpenAI(
    api_key=API_KEY,
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

    return Action(action_type="wait")


# -------------------------
# LLM ACTION (CRITICAL FIX)
# -------------------------
def get_model_action(observation, step):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a warehouse agent. Respond ONLY in JSON with action_type, order_id, item, quantity."
                },
                {
                    "role": "user",
                    "content": str(observation)
                }
            ],
            response_format={"type": "json_object"}
        )

        action_dict = json.loads(response.choices[0].message.content)

        return Action(
            action_type=action_dict.get("action_type", "wait"),
            order_id=action_dict.get("order_id"),
            item=action_dict.get("item"),
            quantity=action_dict.get("quantity")
        )

    except Exception:
        # If LLM fails → fallback
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


if __name__ == "__main__":
    main()