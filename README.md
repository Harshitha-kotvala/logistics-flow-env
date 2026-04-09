# Logistics Flow Environment  
An OpenEnv-Compatible Autonomous Supply Chain Agent Evaluation System

---

## 🧠 Overview

Logistics Flow Environment is a step-based simulation platform designed to evaluate how autonomous agents make real-time decisions under resource and time constraints.

Instead of treating LLMs as simple prompt-response systems, this project places them inside a structured decision-making environment where they must prioritize tasks, manage limited inventory, operate under deadlines, and optimize long-term reward.

The system follows an OpenEnv-compatible architecture, enabling agents to interact through a reinforcement learning-style loop (reset → step → reward → done).

---

## ⚙️ Agent Decision Framework

Agents interact with the environment by selecting actions at each timestep:

- FULFILL — execute an order using available inventory  
- RESTOCK — request incoming inventory with delay  
- WAIT / DELAY / CANCEL — handle constraints dynamically  

Each decision impacts future state, making this a sequential decision-making problem under constraints.

---

## 🎯 Task Design

The environment includes progressively complex scenarios:

- Easy — Single low-priority order to test basic execution  
- Medium — Mixed priorities to test scheduling and prioritization  
- Hard — High-pressure deadlines to test optimal decision sequencing  

These tasks simulate real-world supply chain conditions.

---

## 📊 Evaluation and Reward System

Agents are evaluated using a strictly bounded reward function between 0 and 1:

- Reward based on fulfillment success  
- Penalties for delays and inefficiencies  
- Priority-weighted scoring  

This setup enables consistent benchmarking similar to reinforcement learning environments.

---

## 🧱 System Architecture

### Backend
- FastAPI with Pydantic  
- OpenEnv-compatible step API  
- Custom environment engine (env.py)  
- Task and grading system (tasks.py)  

### AI Layer
- LLM-driven agent using an OpenAI-compatible client  
- Structured prompt-based decision making  
- Proxy-compatible inference pipeline  

### Infrastructure
- Dockerized application  
- Deployed on Hugging Face Spaces  
- Supports local and hosted execution  

---

## 🔄 Agent Interaction Loop

```
RESET → OBSERVATION → ACTION → STEP → REWARD → NEXT STATE → DONE
```

This loop enables evaluation of agent behavior across multiple steps.

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|------------|
| /reset   | POST   | Initialize environment |
| /step    | POST   | Execute agent action |
| /state   | GET    | Retrieve current state |
| /tasks   | GET    | List available tasks |
| /health  | GET    | Health check |
| /docs    | GET    | Swagger UI |

---

## 🧪 Example Requests

### Reset
```json
{
  "task_id": "easy"
}
```

### Step
```json
{
  "order_id": 1,
  "reasoning": "highest priority"
}
```

---

## 🚀 Running Locally

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
python inference.py --url http://localhost:7860
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|------------|
| API_BASE_URL | Yes | LLM proxy endpoint |
| API_KEY | Yes | API key |
| MODEL_NAME | No | Default: gpt-4o-mini |

---

## 🌐 Live Demo

Space: https://huggingface.co/spaces/Harshithakotvala/logistics-flow-env  
Docs: https://harshithakotvala-logistics-flow-env.hf.space/docs  
