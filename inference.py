import os
import json
import urllib.request
from openai import OpenAI

API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY      = os.environ["API_KEY"]
MODEL_NAME   = os.environ.get("MODEL_NAME", "gpt-4o-mini")

base_url = API_BASE_URL.rstrip("/")
print(f"[CONFIG] base_url={base_url} model={MODEL_NAME}")

client = OpenAI(api_key=API_KEY, base_url=base_url)

def priority_value(p):
    return {"high": 3, "medium": 2, "low": 1}.get(p, 0)

def fallback_action(orders):
    if not orders:
        return None
    return sorted(orders, key=lambda o: (o["deadline"], -priority_value(o["priority"])))[0]["id"]

def http_post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def llm_action(orders, step):
    prompt = (
        f"Step {step}. Warehouse orders: {json.dumps(orders)}.\n"
        "Pick ONE order_id to fulfill next (highest priority + nearest deadline).\n"
        'Respond ONLY with JSON: {"order_id": <int>, "reasoning": "<str>"}'
    )
    # REMOVED response_format — LiteLLM proxies often reject it causing silent fallback
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a warehouse fulfillment agent. Respond in JSON only, no markdown."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    content = response.choices[0].message.content.strip()
    # Strip markdown if model wraps in code blocks
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    print(f"  [LLM] {content}")
    return int(json.loads(content)["order_id"])

def run_task(server_url, task_id):
    print(f"[START] {task_id.upper()}")
    try:
        obs = http_post(f"{server_url}/reset", {"task_id": task_id})
    except Exception as e:
        print(f"[END] {task_id.upper()} ERROR={e}")
        return

    for step in range(20):
        orders = obs.get("orders", [])
        done   = obs.get("done", False)
        if done or not orders:
            break

        try:
            order_id = llm_action(orders, step)
        except Exception as e:
            print(f"  [LLM ERROR] {e}")  # Log the REAL error so you can debug
            order_id = fallback_action(orders)

        if order_id is None:
            break

        print(f"[STEP {step}] order_id={order_id}")
        try:
            result = http_post(
                f"{server_url}/step",
                {"order_id": order_id, "reasoning": "LLM decision"}
            )
            obs    = result.get("observation", {})
            reward = result.get("reward", 0)
            done   = result.get("done", False)
            print(f"  reward={reward} done={done}")
        except Exception as e:
            print(f"  [STEP ERROR] {e}")
            break

        if done:
            break

    print(f"[END] {task_id.upper()}")

def main():
    server_url = os.environ.get(
        "SERVER_URL",
        "https://harshithakotvala-logistics-flow-env.hf.space"
    ).rstrip("/")

    for task_id in ["easy", "medium", "hard"]:
        run_task(server_url, task_id)

if __name__ == "__main__":
    main()
