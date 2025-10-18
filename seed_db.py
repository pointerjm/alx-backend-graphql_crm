import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed():
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    alice = Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
    bob = Customer.objects.create(name="Bob", email="bob@example.com")

    laptop = Product.objects.create(name="Laptop", price=999.99, stock=10)
    mouse = Product.objects.create(name="Mouse", price=25.50, stock=100)

    order = Order.objects.create(customer=alice)
    order.products.set([laptop, mouse])
    order.calculate_total()

    print("✅ Seed complete!")

if __name__ == "__main__":
    seed()
