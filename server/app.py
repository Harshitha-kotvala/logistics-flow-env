from fastapi import FastAPI
from env import LogisticsEnv, Action
from tasks import easy_task, medium_task, hard_task

app = FastAPI()
env = LogisticsEnv()

@app.post("/reset")
def reset(task: str = "easy"):
    if task == "easy":
        orders = easy_task()
    elif task == "medium":
        orders = medium_task()
    else:
        orders = hard_task()

    obs = env.reset(orders=orders)

    return {
        "observation": obs.dict(),
        "reward": 0.0,
        "done": False,
        "info": {}
    }

@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.post("/state")
def state():
    obs = env._get_observation()
    return {
        "observation": obs.dict()
    }
def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()