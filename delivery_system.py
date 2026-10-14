"""Food delivery order queue manager."""
import json
from datetime import datetime

VALID_STATUSES = ["placed", "cooking", "out_for_delivery", "delivered"]
DEFAULT_MENU = {"pizza": 250, "burger": 150, "fries": 90, "coke": 40}


class OrderQueue:
    """Holds the orders for one kitchen and the menu prices."""

    def __init__(self, menu=None):
        self.orders = {}
        self.next_id = 1
        self.menu = dict(DEFAULT_MENU) if menu is None else menu

    def read_menu_config(self, file="menu.json"):
        """Load the menu from a JSON file, else use the default menu."""
        try:
            with open(file, encoding="utf-8") as handle:
                self.menu = json.load(handle)
        except (OSError, json.JSONDecodeError):
            self.menu = dict(DEFAULT_MENU)

    def create_order(self, customer, items):
        """Create an order and return its id.

        Raises ValueError on bad input.
        """
        if not customer:
            raise ValueError("customer name is required")
        if not items:
            raise ValueError("an order needs at least one item")
        unknown = [i for i in items if i not in self.menu]
        if unknown:
            raise ValueError(f"not on the menu: {', '.join(unknown)}")
        total = sum(self.menu[i] for i in items)
        order_id = self.next_id
        self.orders[order_id] = {
            "customer": customer,
            "items": items,
            "total": total,
            "status": "placed",
        }
        self.next_id += 1
        return order_id

    def update_order_status(self, order_id, status):
        """Move an order to a new status. Raises ValueError on bad input."""
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid status: {status}")
        if order_id not in self.orders:
            raise ValueError(f"unknown order id: {order_id}")
        self.orders[order_id]["status"] = status

    def daily_revenue(self):
        """Return the total of all delivered orders."""
        return sum(o["total"] for o in self.orders.values()
                   if o["status"] == "delivered")

    def backup_orders(self, file="orders.json"):
        """Write the orders to disk as JSON."""
        with open(file, "w", encoding="utf-8") as handle:
            json.dump({"next_id": self.next_id, "orders": self.orders},
                      handle)

    def restore_orders(self, file="orders.json"):
        """Load orders from disk (JSON keys are strings, so convert to int)."""
        with open(file, encoding="utf-8") as handle:
            data = json.load(handle)
        self.next_id = data["next_id"]
        self.orders = {int(k): v for k, v in data["orders"].items()}

    def print_queue(self):
        print(f"Order queue at {datetime.now()}")
        for order_id, o in self.orders.items():
            print(order_id, o["customer"], o["status"], o["total"])


def main():
    """Run the demo scenario."""
    queue = OrderQueue()
    queue.read_menu_config()
    attempts = [
        ("Asha", ["pizza", "coke"]),
        ("Ravi", ["burger", "sushi"]),
        ("", []),
    ]
    ids = []
    for customer, items in attempts:
        try:
            ids.append(queue.create_order(customer, items))
        except ValueError as err:
            print("Order rejected:", err)
    updates = [
        (ids[0], "delivered"),
        (ids[0], "teleported"),
        (42, "delivered"),
    ]
    for order_id, status in updates:
        try:
            queue.update_order_status(order_id, status)
        except ValueError as err:
            print("Update rejected:", err)
    print("Revenue today:", queue.daily_revenue())
    queue.backup_orders()
    queue.restore_orders()
    queue.print_queue()


if __name__ == "__main__":
    main()
