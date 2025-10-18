#!/usr/bin/env python
import os
import django
from crm.models import Customer, Product, Order
from crm.schema import CreateOrder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

def seed_data():
    # Clear existing data
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()
    
    print("🌱 Seeding database...")
    
    # Create customers
    customers = [
        Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890"),
        Customer.objects.create(name="Bob", email="bob@example.com", phone="123-456-7890"),
        Customer.objects.create(name="Carol", email="carol@example.com"),
    ]
    
    # Create products
    products = [
        Product.objects.create(name="Laptop", price=999.99, stock=10),
        Product.objects.create(name="Mouse", price=29.99, stock=50),
        Product.objects.create(name="Keyboard", price=79.99, stock=25),
    ]
    
    # Create orders
    orders = [
        Order.objects.create(customer=customers[0], total_amount=1029.98),
        Order.objects.create(customer=customers[1], total_amount=109.98),
    ]
    
    # Associate products
    orders[0].products.set([products[0], products[1]])
    orders[1].products.set([products[1], products[2]])
    
    print(f"✅ Seeded:")
    print(f"   {Customer.objects.count()} customers")
    print(f"   {Product.objects.count()} products") 
    print(f"   {Order.objects.count()} orders")

if __name__ == "__main__":
    seed_data()