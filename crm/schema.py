import re
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.utils import timezone
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# --------------------------------------------------------------------
# GRAPHQL TYPES
# --------------------------------------------------------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
        filterset_class = CustomerFilter


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        filterset_class = ProductFilter


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        filterset_class = OrderFilter


# --------------------------------------------------------------------
# MUTATIONS
# --------------------------------------------------------------------
class CreateCustomer(graphene.Mutation):
    """Create a single customer with validation"""
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        # Email uniqueness validation
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        # Phone format validation
        if phone and not re.match(r'^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$', phone):
            raise Exception("Invalid phone number format")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    """Create multiple customers in one transaction with partial success support"""
    class Arguments:
        input = graphene.List(graphene.JSONString, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers = []
        errors = []

        for entry in input:
            try:
                # Convert stringified JSON if necessary
                data = eval(entry) if isinstance(entry, str) else entry

                if Customer.objects.filter(email=data["email"]).exists():
                    errors.append(f"Duplicate email: {data['email']}")
                    continue

                phone = data.get("phone")
                if phone and not re.match(r'^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$', phone):
                    errors.append(f"Invalid phone format: {phone}")
                    continue

                customer = Customer.objects.create(
                    name=data["name"],
                    email=data["email"],
                    phone=phone,
                )
                created_customers.append(customer)
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    """Create a new product"""
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive")
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    """Create a new order and associate products"""
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        # Validate customer
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        # Validate products
        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            raise Exception("Invalid product IDs")

        total = sum(p.price for p in products)
        order = Order.objects.create(
            customer=customer,
            total_amount=total,
            order_date=order_date or timezone.now(),
        )
        order.products.set(products)
        return CreateOrder(order=order)


# --------------------------------------------------------------------
# QUERY FIELDS
# --------------------------------------------------------------------
class Query(graphene.ObjectType):
    """GraphQL query definitions"""
    hello = graphene.String(default_value="Hello, GraphQL!")

    # Simple list queries
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    # Filtered queries using DjangoFilterConnectionField
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()


# --------------------------------------------------------------------
# ROOT MUTATION REGISTRATION
# --------------------------------------------------------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
