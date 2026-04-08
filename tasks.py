from env import Order

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

WEIGHTS = {"low": 1, "medium": 2, "high": 3}

def grade_easy(fulfilled_ids: list, all_orders: list) -> float:
    # Binary but clamped — never exactly 0.0 or 1.0
    total = len(all_orders)
    fulfilled = len(fulfilled_ids)
    raw = fulfilled / total if total > 0 else 0
    return max(0.01, min(0.99, raw))

def grade_medium(fulfilled_ids: list, all_orders: list) -> float:
    total_weight = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
    fulfilled_weight = sum(
        WEIGHTS.get(o.priority, 1) for o in all_orders if o.id in fulfilled_ids
    )
    raw = fulfilled_weight / total_weight if total_weight > 0 else 0
    return max(0.01, min(0.99, raw))

def grade_hard(fulfilled_ids: list, all_orders: list) -> float:
    total_weight = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
    fulfilled_weight = sum(
        WEIGHTS.get(o.priority, 1) for o in all_orders if o.id in fulfilled_ids
    )
    raw = fulfilled_weight / total_weight if total_weight > 0 else 0
    return max(0.01, min(0.99, raw))
