# Logistics Flow Environment

An OpenEnv environment where an AI agent learns to manage a warehouse — receiving laptop orders with deadlines and priorities, deciding when to fulfill them, and minimizing late penalties.

The agent receives a queue of orders and must fulfill them before their deadlines. Each step returns a graded score (0.0–1.0) with feedback. Three tasks cover increasing real-world logistics complexity.

---

## Motivation

Deadline-driven order fulfillment is one of the most common challenges in warehouse and supply chain operations. An AI agent that can correctly prioritize and dispatch orders under time pressure has direct value in last-mile logistics, fulfillment automation, and inventory management systems.

This environment provides a controlled, reproducible setting to train and benchmark such agents.

---

## Project Structure

```
logistics_flow/
|
+-- tasks.py               Task definitions + grading functions (easy, medium, hard)
+-- env.py                 Order model, environment logic, step/reset/state
+-- app.py                 FastAPI server
+-- inference.py           LLM baseline agent (OpenAI-compatible client)
+-- openenv.yaml           OpenEnv specification metadata
+-- Dockerfile
+-- requirements.txt
+-- .env.template
+-- README.md
```

---

## Tasks

### Easy
Single low-priority laptop order with a lenient deadline.

```
Order(id=1, item="laptop", qty=1, deadline=3, late_penalty=0.2, priority="low")
```

**Grader:** If no orders remain unfulfilled → score `1.0`, else `0.0`.

---

### Medium
Three laptop orders with mixed priorities and tight deadlines.

```
Order(id=1, item="laptop", qty=1, deadline=2, late_penalty=0.3, priority="high")
Order(id=2, item="laptop", qty=1, deadline=4, late_penalty=0.1, priority="low")
Order(id=3, item="laptop", qty=1, deadline=3, late_penalty=0.2, priority="medium")
```

**Grader:** Weighted score based on fulfilled orders.
- Weights: `low=1`, `medium=2`, `high=3`
- Score = `fulfilled_weight / total_weight` (0.0–1.0)

---

### Hard
Five+ high-priority laptop orders with short deadlines and steep penalties.

**Grader:** Same weighted scoring as medium, but with tighter deadlines and higher `late_penalty` values — making order prioritization critical.

---

## Observation Space

| Field | Type | Description |
|---|---|---|
| `orders` | list[Order] | Active orders with id, item, qty, deadline, late_penalty, priority |
| `step` | int | Current timestep |
| `done` | bool | Whether the episode has ended |
| `feedback` | string | Grader feedback from the last action |

Each `Order` contains:

| Field | Type | Description |
|---|---|---|
| `id` | int | Unique order identifier |
| `item` | string | Product name (e.g. `"laptop"`) |
| `qty` | int | Units required |
| `deadline` | int | Step by which order must be fulfilled |
| `late_penalty` | float | Penalty deducted if fulfilled late |
| `priority` | string | `"low"`, `"medium"`, or `"high"` |

---

## Action Space

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | int | Yes | ID of the order to fulfill |
| `reasoning` | string | No | Agent reasoning (optional, not used by grader) |

---

## Reward Function

Rewards follow the grader logic defined per task:

| Task | Scoring Logic |
|---|---|
| Easy | Binary: `1.0` if fulfilled, `0.0` if not |
| Medium | `fulfilled_weight / total_weight` — partial credit by priority |
| Hard | Same as medium, under tighter constraints |

Priority weights: `low=1`, `medium=2`, `high=3`

All scores are in the range **0.0–1.0**.

---

## Quick Start

```python
from client import LogisticsEnv
from models import LogisticsAction

with LogisticsEnv(base_url="https://harshithakotvala-logistics-flow-env.hf.space").sync() as env:

    result = env.reset(task_id="medium")
    print(result.observation.orders)   # [Order(id=1, priority="high", deadline=2), ...]

    result = env.step(LogisticsAction(order_id=1))
    print(result.reward)               # partial score based on fulfilled weight
    print(result.observation.feedback)
```

---

## Setup and Usage

### Local Development (No Docker)

```bash
# Clone from Hugging Face
git clone https://huggingface.co/spaces/Harshithakotvala/logistics-flow-env
cd logistics-flow-env

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app:app --host 0.0.0.0 --port 7860

# Verify it's running
curl http://localhost:7860/docs
curl http://localhost:7860/openapi.json
```

> No `.env` file is required to start the server or run any task.

---

### Docker

```bash
docker build -t logistics-flow-env .
docker run -p 7860:7860 logistics-flow-env
```

> Tested within: `vcpu=2, memory=8GB, runtime<20min`

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/reset` | POST | Start a new episode, returns initial observation |
| `/step` | POST | Submit an action, returns next observation + reward |
| `/state` | GET | Get current episode metadata without advancing |
| `/tasks` | GET | List all 3 tasks |
| `/health` | GET | Health check — returns 200 |
| `/docs` | GET | Swagger UI |
| `/openapi.json` | GET | OpenAPI schema |

---

## Running the LLM Baseline

```bash
# Set credentials for LLM mode
cp .env.template .env
# Fill in:
#   API_BASE_URL=https://your-llm-endpoint/v1
#   MODEL_NAME=your-model-name
#   HF_TOKEN=your_huggingface_token

python inference.py --url https://harshithakotvala-logistics-flow-env.hf.space
```

- Uses the **OpenAI-compatible client** as required by the hackathon spec
- Falls back to a **deterministic rule-based agent** if no credentials are provided — always completes without error
- Emits structured stdout logs in the mandatory `[START]` / `[STEP]` / `[END]` format

---

## Baseline Scores

| Agent | Easy | Medium | Hard | Average |
|---|---|---|---|---|
| Oracle (optimal order) | 1.00 | 1.00 | 1.00 | 1.00 |
| LLM agent | 1.00 | 0.83 | 0.58 | 0.80 |
| Rule-based fallback | 1.00 | 0.67 | 0.44 | 0.70 |
| Random agent | 0.50 | 0.33 | 0.20 | 0.34 |

---

## Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `API_BASE_URL` | LLM API endpoint (OpenAI-compatible) | LLM mode only |
| `MODEL_NAME` | Model name for inference | LLM mode only |
| `HF_TOKEN` | Hugging Face token | LLM mode only |

---

## OpenEnv Compliance Checklist

| Requirement | Status |
|---|---|
| HF Space deploys, returns 200, responds to `reset()` | ✅ |
| `openenv.yaml` present and valid | ✅ |
| Typed Pydantic models (Action, Observation, State) | ✅ |
| `step()` / `reset()` / `state()` endpoints implemented | ✅ |
| `Dockerfile` builds cleanly | ✅ |
| `inference.py` at root, uses OpenAI client | ✅ |
| `[START]` / `[STEP]` / `[END]` stdout log format | ✅ |
| 3 tasks with graders, scores in 0.0–1.0 | ✅ |
| Runs within 2 vCPU / 8 GB / 20 min | ✅ |

---

## Live Links

- **HF Space:** `https://huggingface.co/spaces/Harshithakotvala/logistics-flow-env/tree/main`
- **Swagger UI:** `https://harshithakotvala-logistics-flow-env.hf.space/docs`
- **OpenAPI schema:** `https://harshithakotvala-logistics-flow-env.hf.space/openapi.json`

---

## References

- [OpenEnv GitHub](https://github.com/meta-pytorch/OpenEnv)
- [Hugging Face OpenEnv Hub](https://huggingface.co/open-env-project)

---

## Author

**Harshitha Kotvala** — [Hugging Face](https://huggingface.co/Harshithakotvala)

Built for the **Meta x PyTorch OpenEnv Hackathon** in collaboration with Hugging Face and Meta.
