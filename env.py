print("FILE IS RUNNING")

from pydantic import BaseModel
from typing import List, Dict, Optional
import enum

# -------------------------
# ENUMS
# -------------------------
class ActionType(str, enum.Enum):
    FULFILL = "fulfill"
    RESTOCK = "restock"
    DELAY = "delay"
    PRIORITIZE = "prioritize"
    CANCEL = "cancel"
    WAIT = "wait"


# -------------------------
# MODELS
# -------------------------
class Action(BaseModel):
    action_type: ActionType
    order_id: Optional[int] = None
    item: Optional[str] = None
    quantity: Optional[int] = None


class Order(BaseModel):
    id: int
    item: str
    qty: int
    deadline: int
    late_penalty: float
    priority: str


class InboundShipment(BaseModel):
    item: str
    qty: int
    arrival_step: int


class Observation(BaseModel):
    inventory: Dict[str, int]
    orders: List[Order]
    delayed_orders: List[Order]
    inbound_shipments: List[InboundShipment]
    current_step: int
    total_penalty: float
    fulfilled_orders: int
    action_history: List[Dict]   # 🔥 NEW FEATURE


# -------------------------
# ENVIRONMENT
# -------------------------
class LogisticsEnv:
    def __init__(self):
        self.reset()

    def reset(self, orders=None):
        self.current_step = 0

        self.inventory = {
            "laptop": 2,
            "phone": 3
        }

        if orders:
            self.orders = orders
        else:
            self.orders = [
                Order(id=1, item="laptop", qty=1, deadline=3, late_penalty=0.2, priority="high"),
                Order(id=2, item="phone", qty=2, deadline=4, late_penalty=0.1, priority="low")
            ]

        self.delayed_orders = []
        self.inbound_shipments = []

        self.total_penalty = 0.0
        self.fulfilled_orders = 0

        self.action_history = []   # 🔥 INIT HISTORY

        return self._get_observation()

    def _get_observation(self):
        return Observation(
            inventory=self.inventory,
            orders=self.orders,
            delayed_orders=self.delayed_orders,
            inbound_shipments=self.inbound_shipments,
            current_step=self.current_step,
            total_penalty=self.total_penalty,
            fulfilled_orders=self.fulfilled_orders,
            action_history=self.action_history
        )

    def _check_done(self):
        return len(self.orders) == 0 and len(self.inbound_shipments) == 0

    def step(self, action: Action):
        reward = 0.0
        info = {}

        # -------------------------
        # 🔥 LOG ACTION
        # -------------------------
        self.action_history.append({
            "step": self.current_step,
            "action": action.action_type,
            "order_id": action.order_id,
            "item": action.item,
            "quantity": action.quantity
        })

        # -------------------------
        # 1. Process inbound shipments
        # -------------------------
        for shipment in self.inbound_shipments[:]:
            if shipment.arrival_step == self.current_step:
                self.inventory[shipment.item] += shipment.qty
                self.inbound_shipments.remove(shipment)

        # -------------------------
        # 2. Apply action
        # -------------------------
        if action.action_type == ActionType.FULFILL:
            order = next((o for o in self.orders if o.id == action.order_id), None)

            if not order:
                reward -= 1
                info["error"] = "Invalid order_id"

            elif self.inventory.get(order.item, 0) >= order.qty:
                self.inventory[order.item] -= order.qty
                self.orders.remove(order)
                self.fulfilled_orders += 1

                if order.priority == "high":
                    reward += 1.5
                elif order.priority == "medium":
                    reward += 1.0
                else:
                    reward += 0.5
            else:
                reward -= 1.0

        elif action.action_type == ActionType.RESTOCK:
            if not action.item or not action.quantity:
                reward -= 1
                info["error"] = "Invalid restock input"
            else:
                arrival = self.current_step + 2
                self.inbound_shipments.append(
                    InboundShipment(item=action.item, qty=action.quantity, arrival_step=arrival)
                )
                reward -= 0.2

        elif action.action_type == ActionType.DELAY:
            order = next((o for o in self.orders if o.id == action.order_id), None)
            if order:
                self.orders.remove(order)
                self.delayed_orders.append(order)
                reward -= 0.5

        elif action.action_type == ActionType.CANCEL:
            order = next((o for o in self.orders if o.id == action.order_id), None)
            if order:
                self.orders.remove(order)
                reward -= 0.3

        elif action.action_type == ActionType.PRIORITIZE:
            order = next((o for o in self.orders if o.id == action.order_id), None)
            if order:
                order.priority = "high"
                reward -= 0.3

        elif action.action_type == ActionType.WAIT:
            reward -= 0.1

        # -------------------------
        # 3. Deadline penalties
        # -------------------------
        for order in self.orders:
            if self.current_step > order.deadline:
                self.total_penalty += order.late_penalty
                reward -= order.late_penalty

        # -------------------------
        # 4. Holding cost
        # -------------------------
        total_inventory = sum(self.inventory.values())
        reward -= 0.05 * total_inventory

        # -------------------------
        # 5. Increment step
        # -------------------------
        self.current_step += 1

        # -------------------------
        # 6. Done
        # -------------------------
        done = self._check_done()

        reward = round(min(0.99, max(0.01, float(reward))), 6)
        return self._get_observation(), reward, done, info


# -------------------------
# TEST RUN
# -------------------------
if __name__ == "__main__":
    env = LogisticsEnv()

    obs = env.reset()
    print("Initial:", obs)

    action = Action(action_type=ActionType.FULFILL, order_id=1)
    obs, reward, done, info = env.step(action)

    print("\nAfter Step:")
    print("Observation:", obs)
    print("Reward:", reward)
    print("Done:", done)
    print("Info:", info)
