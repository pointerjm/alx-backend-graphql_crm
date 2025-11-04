# crm/cron_jobs/send_order_reminders.py

import os
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# === Windows-safe log path ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'order_reminders_log.txt')

def main():
    # DISABLE schema fetching
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        # No use_schema, no fetch_schema
    )

    # CRITICAL: Set fetch_schema=False
    client = Client(
        transport=transport,
        fetch_schema=False  # This stops the error
    )

    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)

    query = gql(f'''
    query {{
      allOrders(orderDate_Gte: "{week_ago}", orderDate_Lte: "{today}") {{
        edges {{
          node {{
            id
            customer {{ email }}
          }}
        }}
      }}
    }}
    ''')

    try:
        result = client.execute(query)
        timestamp = datetime.datetime.now().isoformat()

        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            for edge in result['allOrders']['edges']:
                order = edge['node']
                f.write(f"{timestamp} - Order {order['id']} → {order['customer']['email']}\n")
        print("Order reminders processed!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()