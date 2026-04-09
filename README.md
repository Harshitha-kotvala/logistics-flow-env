# Logistics Flow Environment

A warehouse order fulfillment environment built for the Meta x PyTorch OpenEnv Hackathon. An AI agent receives laptop orders with deadlines and priorities, decides which to fulfill at each step, and is scored on how well it manages fulfillment under time pressure.

---

## Overview

Real-world warehouses face constant pressure to fulfill orders before deadlines while balancing priorities. This environment simulates that challenge in a controlled, reproducible setting — making it useful for training and benchmarking RL agents on logistics tasks.


## Project Structure

```
logistics-flow-env/
├── app.py              # Main FastAPI application
├── server/app.py       # Server entrypoint
├── env.py              # Environment logic and models
├── tasks.py            # Task definitions and graders
├── inference.py        # LLM agent using OpenAI-compatible client
├── openenv.yaml        # OpenEnv specification
├── Dockerfile
└── requirements.txt
```
## Tasks

Three tasks of increasing difficulty, all involving laptop orders:

**Easy** — One low-priority order, generous deadline. Tests basic fulfillment.

**Medium** — Three orders with mixed priorities and tighter deadlines. Tests prioritization.

**Hard** — Five high-priority orders with very short deadlines and steep penalties. Tests optimal ordering under pressure.

---

## API

| Endpoint | Method | Description |
|---|---|---|
| `/reset` | POST | Begin a new episode |
| `/step` | POST | Fulfill an order |
| `/state` | GET | View current episode state |
| `/tasks` | GET | List available tasks |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |

### Reset Request
```json
{"task_id": "easy"}
```

### Step Request
```json
{"order_id": 1, "reasoning": "highest priority"}
```

---

## Observation Space

| Field | Type | Description |
|---|---|---|
| `orders` | list | Active orders with id, item, qty, deadline, penalty, priority |
| `step` | int | Current timestep |
| `done` | bool | Episode complete |
| `feedback` | string | Action feedback |

---

## Scoring

Scores are always strictly between 0 and 1. Higher scores mean better fulfillment:

- **Easy** — proportional to orders fulfilled
- **Medium** — weighted by priority (high=3, medium=2, low=1)
- **Hard** — same weighted scoring under tighter constraints

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app:app --host 0.0.0.0 --port 7860

# Run inference agent
python inference.py --url http://localhost:7860
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_BASE_URL` | Yes | OpenAI-compatible LLM endpoint |
| `API_KEY` | Yes | API key |
| `MODEL_NAME` | No | Model to use (default: gpt-4o-mini) |

---

## Live

- **Space:** https://huggingface.co/spaces/Harshithakotvala/logistics-flow-env
- **Docs:** https://harshithakotvala-logistics-flow-env.hf.space/docs
