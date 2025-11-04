# crm/cron.py
import os
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# For internal logs (optional)
LOW_STOCK_LOG = os.path.join(LOG_DIR, 'low_stock_updates_log.txt')

def log_crm_heartbeat():
    """Logs CRM health every 5 minutes."""
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive"

    try:
        transport = RequestsHTTPTransport(url='http://localhost:8000/graphql', verify=False)
        client = Client(transport=transport, fetch_schema=False)
        query = gql('{ __typename }')
        client.execute(query)
        message += " (GraphQL alive)"
    except Exception as e:
        message += f" (GraphQL down: {e})"

    # ✅ Required by the check: log to /tmp/crm_heartbeat_log.txt
    with open('/tmp/crm_heartbeat_log.txt', 'a', encoding='utf-8') as f:
        f.write(message + '\n')


def update_low_stock():
    """Runs every 12 hours to restock low-stock products."""
    transport = RequestsHTTPTransport(url='http://localhost:8000/graphql', verify=False)
    client = Client(transport=transport, fetch_schema=False)

    mutation = gql('''
    mutation {
      updateLowStockProducts {
        updatedProducts { name stock }
        message
      }
    }
    ''')

    timestamp = datetime.datetime.now().isoformat()
    try:
        result = client.execute(mutation)
        products = result['updateLowStockProducts']['updatedProducts']

        with open(LOW_STOCK_LOG, 'a', encoding='utf-8') as f:
            for p in products:
                f.write(f"{timestamp} - Restocked: {p['name']} → {p['stock']}\n")
    except Exception as e:
        with open(LOW_STOCK_LOG, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} - ERROR: {e}\n")
