# crm/cron.py
import os
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


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

    with open('/tmp/crm_heartbeat_log.txt', 'a', encoding='utf-8') as f:
        f.write(message + '\n')


def update_low_stock():
    """Runs every 12 hours to restock low-stock products."""
    timestamp = datetime.datetime.now().isoformat()
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

    try:
        result = client.execute(mutation)
        products = result['updateLowStockProducts']['updatedProducts']

        with open('/tmp/low_stock_updates_log.txt', 'a', encoding='utf-8') as f:  # ✅ fixed path
            for p in products:
                f.write(f"{timestamp} - Restocked: {p['name']} → {p['stock']}\n")
    except Exception as e:
        with open('/tmp/low_stock_updates_log.txt', 'a', encoding='utf-8') as f:  # ✅ fixed path
            f.write(f"{timestamp} - ERROR: {e}\n")
