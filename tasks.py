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

def grade_easy(env) -> float:
    try:
        remaining = len(env.orders)
        total = len(easy_task())
        fulfilled = max(0, total - remaining)
        score = min(1.0, max(0.0, fulfilled / total)) if total > 0 else 0
        return round(0.1 + score * 0.8, 4)
    except Exception:
        return 0.5

def grade_medium(env) -> float:
    try:
        all_orders = medium_task()
        remaining_ids = {o.id for o in env.orders}
        total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
        done_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id not in remaining_ids)
        score = min(1.0, max(0.0, done_w / total_w)) if total_w > 0 else 0
        return round(0.1 + score * 0.8, 4)
    except Exception:
        return 0.5

def grade_hard(env) -> float:
    try:
        all_orders = hard_task()
        remaining_ids = {o.id for o in env.orders}
        total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
        done_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id not in remaining_ids)
        score = min(1.0, max(0.0, done_w / total_w)) if total_w > 0 else 0
        return round(0.1 + score * 0.8, 4)
    except Exception:
        return 0.5
