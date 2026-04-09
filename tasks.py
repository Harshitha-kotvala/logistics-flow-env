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
    remaining = len(env.orders)
    if remaining == 0:
        return 0.95   # all fulfilled
    return 0.05       # nothing fulfilled


def grade_medium(env) -> float:
    all_orders = medium_task()
    remaining_ids = {o.id for o in env.orders}
    total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
    done_w  = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id not in remaining_ids)

    if done_w == 0:
        return 0.05
    if done_w == total_w:
        return 0.95
    # partial — safe values between 0.1 and 0.9
    ratio = done_w / total_w
    return round(0.1 + ratio * 0.8, 4)


def grade_hard(env) -> float:
    all_orders = hard_task()
    remaining_ids = {o.id for o in env.orders}
    total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
    done_w  = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id not in remaining_ids)

    if done_w == 0:
        return 0.05
    if done_w == total_w:
        return 0.95
    ratio = done_w / total_w
    return round(0.1 + ratio * 0.8, 4)
