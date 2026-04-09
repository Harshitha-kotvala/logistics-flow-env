def grade_easy(env) -> float:
    try:
        remaining = len(env.orders)
        total = 1
        score = (total - remaining) / total
        # Map to (0.1, 0.9) range - never 0 or 1
        return round(0.1 + score * 0.8, 4)
    except Exception:
        return 0.5

def grade_medium(env) -> float:
    try:
        all_orders = medium_task()
        remaining_ids = {o.id for o in env.orders}
        total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
        done_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id not in remaining_ids)
        score = done_w / total_w if total_w > 0 else 0
        return round(0.1 + score * 0.8, 4)
    except Exception:
        return 0.5

def grade_hard(env) -> float:
    try:
        all_orders = hard_task()
        remaining_ids = {o.id for o in env.orders}
        total_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders)
        done_w = sum(WEIGHTS.get(o.priority, 1) for o in all_orders if o.id not in remaining_ids)
        score = done_w / total_w if total_w > 0 else 0
        return round(0.1 + score * 0.8, 4)
    except Exception:
        return 0.5
