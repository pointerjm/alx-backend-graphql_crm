#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Script: send_order_reminders.py
# Purpose: Query GraphQL endpoint for orders within last 7 days
# Logs reminders to /tmp/order_reminders_log.txt
# ---------------------------------------------------------------------------

import datetime
import requests

GRAPHQL_URL = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

query = """
query {
  allOrders(ordering: "-order_date") {
    edges {
      node {
        id
        orderDate
        customer {
          email
        }
      }
    }
  }
}
"""

def get_recent_orders():
    response = requests.post(GRAPHQL_URL, json={"query": query})
    response.raise_for_status()
    data = response.json()
    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(days=7)

    recent_orders = []
    for edge in data.get("data", {}).get("allOrders", {}).get("edges", []):
        node = edge.get("node", {})
        order_date_str = node.get("orderDate")
        if order_date_str:
            try:
                order_date = datetime.datetime.fromisoformat(order_date_str)
                if order_date >= week_ago:
                    recent_orders.append(node)
            except Exception:
                continue
    return recent_orders

def log_reminders(orders):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for order in orders:
            f.write(f"[{timestamp}] Reminder → Order {order['id']} | Customer: {order['customer']['email']}\n")

if __name__ == "__main__":
    try:
        recent_orders = get_recent_orders()
        log_reminders(recent_orders)
        print("Order reminders processed!")
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] ERROR: {e}\n")
