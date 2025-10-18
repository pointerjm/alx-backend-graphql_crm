from crm.models import Customer, Product

Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
Customer.objects.create(name="Bob", email="bob@example.com")

Product.objects.create(name="Laptop", price=999.99, stock=10)
Product.objects.create(name="Mouse", price=49.99, stock=50)
print("Database seeded successfully.")
