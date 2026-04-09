from env import Order

WEIGHTS = {"low": 1, "medium": 2, "high": 3}

def easy_task():
    return [
        Order(id=1, item="laptop", qty=1, deadline=3, late_penalty=0.2, priority="low")
    ]

def medium_task():
    return [
        Order(id=1, item="laptop", qty=1, deadline=2, late_penalty=0.3, priority="high"),
        Order(id=2, item="laptop", qty=1, deadline=4, late_penalty=0.1, priority="low"),
        Order(id=3, item="laptop", qty=1, deadline=3, late_penalty=0.2, priority="medium"),
    ]

def hard_task():
    return [
        Order(id=1, item="laptop", qty=1, deadline=1, late_penalty=0.5, priority="high"),
        Order(id=2, item="laptop", qty=1, deadline=2, late_penalty=0.4, priority="high"),
        Order(id=3, item="laptop", qty=1, deadline=2, late_penalty=0.4, priority="high"),
        Order(id=4, item="laptop", qty=1, deadline=3, late_penalty=0.3, priority="medium"),
        Order(id=5, item="laptop", qty=1, deadline=4, late_penalty=0.2, priority="low"),
    ]

def _safe(val):
    return min(0.99, max(0.01, float(val)))

# Graders accept EITHER env object OR dict - handles both cases
def grade_easy(env_or_result) -> float:
    try:
        # Try as env object first
        remaining = len(env_or_result.orders)
        if remaining == 0:
            return 0.95
        return 0.05
    except AttributeError:
        # Judge passed a result dict
        if env_or_result.get("remaining_orders", 1) == 0:
            return 0.95
        return 0.05

def grade_medium(env_or_result) -> float:
    try:
        all_orders = medium_task()
        remaining_ids = {o.id for o in env_or_result.orders}
        total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
        done_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id not in remaining_ids)
        if done_w == 0:
            return 0.05
        if done_w == total_w:
            return 0.95
        return _safe(0.1 + (done_w / total_w) * 0.8)
    except AttributeError:
        remaining = env_or_result.get("remaining_orders", 1)
        total = len(medium_task())
        done = total - remaining
        if done == 0:
            return 0.05
        if done >= total:
            return 0.95
        return _safe(0.1 + (done / total) * 0.8)

def grade_hard(env_or_result) -> float:
    try:
        all_orders = hard_task()
        remaining_ids = {o.id for o in env_or_result.orders}
        total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
        done_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id not in remaining_ids)
        if done_w == 0:
            return 0.05
        if done_w == total_w:
            return 0.95
        return _safe(0.1 + (done_w / total_w) * 0.8)
    except AttributeError:
        remaining = env_or_result.get("remaining_orders", 1)
        total = len(hard_task())
        done = total - remaining
        if done == 0:
            return 0.05
        if done >= total:
            return 0.95
        return _safe(0.1 + (done / total) * 0.8)
