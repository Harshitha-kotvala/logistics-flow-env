from env import Order

# -------------------------
# CONSTANTS & HELPERS
# -------------------------
WEIGHTS = {"low": 1, "medium": 2, "high": 3}

def _safe(raw):
    """Ensures reward is strictly between 0 and 1 (banned: 0.0, 1.0)"""
    val = float(raw)
    if val <= 0.0:
        return 0.01
    if val >= 1.0:
        return 0.99
    # Keep precision clean for the validator
    return max(0.01, min(0.99, round(val, 6)))

# -------------------------
# TASK DEFINITIONS
# -------------------------
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

# -------------------------
# GRADERS
# -------------------------
def grade_easy(env) -> float:
    total = len(easy_task())
    fulfilled = getattr(env, 'fulfilled_orders', 0)
    score = fulfilled / total if total > 0 else 0.0
    return _safe(score)

def grade_medium(env) -> float:
    total = len(medium_task())
    fulfilled = getattr(env, 'fulfilled_orders', 0)
    score = fulfilled / total if total > 0 else 0.0
    return _safe(score)

def grade_hard(env) -> float:
    total = len(hard_task())
    fulfilled = getattr(env, 'fulfilled_orders', 0)
    score = fulfilled / total if total > 0 else 0.0
    return _safe(score)
