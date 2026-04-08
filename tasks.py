from env import Order

def easy_task():
    return [
        Order(id=1, item="laptop", qty=1, deadline=3, late_penalty=0.2, priority="low")
    ]

def grade_easy(final_orders):
    if len(final_orders) == 0:
        return 0.99
    return 0.01

def medium_task():
    return [
        Order(id=1, item="laptop", qty=1, deadline=2, late_penalty=0.3, priority="high"),
        Order(id=2, item="laptop", qty=1, deadline=4, late_penalty=0.1, priority="low"),
        Order(id=3, item="laptop", qty=1, deadline=3, late_penalty=0.2, priority="medium"),
    ]

def grade_medium(initial_orders, final_orders):
    weights = {"low": 1, "medium": 2, "high": 3}
    total = sum(weights[o.priority] for o in initial_orders)
    final_ids = {o.id for o in final_orders}
    fulfilled = sum(
        weights[o.priority]
        for o in initial_orders
        if o.id not in final_ids
    )
    score = fulfilled / total if total > 0 else 0.01
    return round(max(0.01, min(0.99, score)), 2)

def hard_task():
    return [
        Order(id=1, item="laptop", qty=1, deadline=3, late_penalty=0.5, priority="high"),
        Order(id=2, item="laptop", qty=1, deadline=5, late_penalty=0.2, priority="low"),
    ]

def grade_hard(total_orders, fulfilled_count, total_penalty):
    if total_orders == 0:
        return 0.01
    base_score = fulfilled_count / total_orders
    penalty_drain = total_penalty / 15.0
    score = base_score - penalty_drain
    return round(max(0.01, min(0.99, score)), 2)
