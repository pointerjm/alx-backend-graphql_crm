#!/bin/bash
# ---------------------------------------------------------------------------
# Script: clean_inactive_customers.sh
# Purpose: Delete customers with no orders in the last year
# Logs deletions with timestamps to /tmp/customer_cleanup_log.txt
# ---------------------------------------------------------------------------

# Activate virtual environment if needed
# source /path/to/venv/bin/activate

cd "$(dirname "$0")/../.." || exit

timestamp=$(date '+%Y-%m-%d %H:%M:%S')
log_file="/tmp/customer_cleanup_log.txt"

deleted_count=$(python3 manage.py shell -c "
from crm.models import Customer
from datetime import timedelta, datetime
from django.utils import timezone

cutoff_date = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(order__order_date__gte=cutoff_date)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

echo \"[$timestamp] Deleted \$deleted_count inactive customers\" >> \$log_file
