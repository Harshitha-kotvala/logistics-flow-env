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

def _safe(raw):
    val = float(raw)
    if val <= 0.0:
        return 0.01
    if val >= 1.0:
        return 0.99
    return round(val, 6)

def grade_easy(env) -> float:
    all_orders = easy_task()
    total_w = len(all_orders)
    remaining_ids = {o.id for o in env.orders}
    fulfilled_w = sum(1 for o in all_orders if o.id not in remaining_ids)
    return _safe(fulfilled_w / total_w)

def grade_medium(env) -> float:
    all_orders = medium_task()
    total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
    remaining_ids = {o.id for o in env.orders}
    fulfilled_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id not in remaining_ids)
    return _safe(fulfilled_w / total_w)

def grade_hard(env) -> float:
    all_orders = hard_task()
    total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
    remaining_ids = {o.id for o in env.orders}
    fulfilled_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id not in remaining_ids)
    return _safe(fulfilled_w / total_w)
