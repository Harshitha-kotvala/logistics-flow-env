import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.getenv("API_KEY", "dummy-key")

# -------------------------
# OpenAI client — safe init
# -------------------------
client = None

def get_client():
    global client
    if client is not None:
        return client
    if not API_BASE_URL:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE_URL
        )
        return client
    except Exception:
        return None


# -------------------------
# HTTP helper using urllib (stdlib only)
# -------------------------
def http_post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


# -------------------------
# Priority helper
# -------------------------
def priority_value(p):
    return {"high": 3, "medium": 2, "low": 1}.get(p, 0)


# -------------------------
# Fallback: rule-based agent
# -------------------------
def fallback_action(orders):
    if not orders:
        return None
    sorted_orders = sorted(
        orders,
        key=lambda o: (o["deadline"], -priority_value(o["priority"]))
    )
    return sorted_orders[0]["id"]


# -------------------------
# LLM action
# -------------------------
def llm_action(orders, step):
    c = get_client()
    if c is None:
        return fallback_action(orders)
    try:
        prompt = (
            f"Step {step}. Orders: {json.dumps(orders)}. "
            "Pick the best order_id to fulfill. "
            'Respond ONLY with JSON: {"order_id": <int>, "reasoning": "<str>"}'
        )
        response = c.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a warehouse fulfillment agent."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return int(data["order_id"])
    except Exception:
        return fallback_action(orders)


# -------------------------
# Run one task via HTTP API
# -------------------------
def run_task(base_url, task_id):
    print(f"[START] task_id={task_id}")

    obs = http_post(f"{base_url}/reset", {"task_id": task_id})

    for step in range(20):
        orders = obs.get("orders", [])
        done = obs.get("done", False)

        if done or not orders:
            break

        order_id = llm_action(orders, step) if API_BASE_URL else fallback_action(orders)

        if order_id is None:
            break

        print(f"[STEP {step}] order_id={order_id}")

        result = http_post(
            f"{base_url}/step",
            {"order_id": order_id, "reasoning": "Prioritized by deadline and priority"}
        )

        obs = result.get("observation", {})
        reward = result.get("reward", 0)
        done = result.get("done", False)

        print(f"  reward={reward} done={done}")

        if done:
            break

    print(f"[END] task_id={task_id}")


# -------------------------
# Main
# -------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Base URL of the logistics env")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")

    for task_id in ["easy", "medium", "hard"]:
        try:
            run_task(base_url, task_id)
        except Exception as e:
            print(f"[ERROR] task_id={task_id} failed: {e}")


if __name__ == "__main__":
    main()