# crm/cron.py

import os
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

HEARTBEAT_LOG = os.path.join(LOG_DIR, 'crm_heartbeat_log.txt')
LOW_STOCK_LOG = os.path.join(LOG_DIR, 'low_stock_updates_log.txt')

def log_crm_heartbeat():
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive"

    try:
        transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')
        client = Client(transport=transport, fetch_schema=False)  # Add this
        query = gql('{ __typename }')
        client.execute(query)
        message += " (GraphQL alive)"
    except Exception as e:
        message += f" (GraphQL down: {e})"

    with open(HEARTBEAT_LOG, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def update_low_stock():
    transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')
    client = Client(transport=transport, fetch_schema=False)  # Add this

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
        timestamp = datetime.datetime.now().isoformat()

        with open(LOW_STOCK_LOG, 'a', encoding='utf-8') as f:
            for p in products:
                f.write(f"{timestamp} - Restocked: {p['name']} → {p['stock']}\n")
    except Exception as e:
        with open(LOW_STOCK_LOG, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.datetime.now().isoformat()} - ERROR: {e}\n")