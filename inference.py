import os
import json
import argparse
import urllib.request
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_BASE_URL = os.environ.get("API_BASE_URL", "").rstrip("/")
MODEL_NAME   = os.environ.get("MODEL_NAME", "gpt-4o-mini")
API_KEY      = os.environ.get("API_KEY", "dummy-key")

# Must use OpenAI client per hackathon rules
client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL if API_BASE_URL else "https://api.openai.com/v1"
)

# -------------------------
# HTTP helper for env API
# -------------------------
def http_post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

# -------------------------
# Helpers
# -------------------------
def priority_value(p):
    return {"high": 3, "medium": 2, "low": 1}.get(p, 0)

def fallback_action(orders):
    if not orders:
        return None
    return sorted(orders, key=lambda o: (o["deadline"], -priority_value(o["priority"])))[0]["id"]

# -------------------------
# LLM action via OpenAI client
# -------------------------
def llm_action(orders, step):
    try:
        prompt = (
            f"Step {step}. Warehouse orders: {json.dumps(orders)}.\n"
            "Pick ONE order_id to fulfill next (highest priority + nearest deadline).\n"
            'Respond ONLY with JSON: {"order_id": <int>, "reasoning": "<str>"}'
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a warehouse fulfillment agent. Respond in JSON only."},
                {"role": "user",   "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return int(json.loads(content)["order_id"])
    except Exception as e:
        print(f"  [LLM fallback] {e}")
        return fallback_action(orders)

# -------------------------
# Run one task
# -------------------------
def run_task(base_url, task_id):
    print(f"[START] {task_id.upper()}")

    obs = http_post(f"{base_url}/reset", {"task_id": task_id})

    for step in range(20):
        orders = obs.get("orders", [])
        done   = obs.get("done", False)

        if done or not orders:
            break

        order_id = llm_action(orders, step)
        if order_id is None:
            break

        print(f"[STEP {step}] order_id={order_id}")

        result = http_post(
            f"{base_url}/step",
            {"order_id": order_id, "reasoning": "Chosen by LLM based on deadline and priority"}
        )

        obs    = result.get("observation", {})
        reward = result.get("reward", 0)
        done   = result.get("done", False)
        print(f"  reward={reward} done={done} feedback={obs.get('feedback','')}")

        if done:
            break

    print(f"[END] {task_id.upper()}")

# -------------------------
# Main
# -------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        default="https://harshithakotvala-logistics-flow-env.hf.space",
        help="Base URL of the logistics env"
    )
    args = parser.parse_args()
    base_url = args.url.rstrip("/")

    for task_id in ["easy", "medium", "hard"]:
        try:
            run_task(base_url, task_id)
        except Exception as e:
            print(f"[ERROR] task={task_id}: {e}")

if __name__ == "__main__":
    main()