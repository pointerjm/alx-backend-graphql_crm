import graphene
from graphene import ObjectType, String, Float, Int, ID, List, Field, Boolean, DateTime
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter  # ✅ ADDED FILTERS
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime
import re

# Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        fields = ('id', 'name', 'email', 'phone', 'created_at')

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        fields = ('id', 'name', 'price', 'stock', 'created_at')

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        fields = ('id', 'total_amount', 'order_date')

    customer = graphene.Field(CustomerType)
    products = graphene.List(ProductType)

    def resolve_customer(self, info):
        return self.customer

    def resolve_products(self, info):
        return self.products.all()

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = String(required=True)
    email = String(required=True)
    phone = String()

class ProductInput(graphene.InputObjectType):
    name = String(required=True)
    price = Float(required=True)
    stock = Int(default_value=0)

class OrderInput(graphene.InputObjectType):
    customer_id = ID(required=True)
    product_ids = List(ID, required=True)

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = String()
    success = Boolean()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            # Validate phone format
            if input.phone and not re.match(r'^\+?1?[-\.\s]?\(?([0-9]{3})\)?[-\.\s]?([0-9]{3})[-\.\s]?([0-9]{4})$', input.phone):
                raise ValidationError("Invalid phone format")

            # Check email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                raise ValidationError("Email already exists")

            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone or ""
            )
            return CreateCustomer(customer=customer, message="Customer created successfully", success=True)
        except ValidationError as e:
            return CreateCustomer(customer=None, message=str(e), success=False)
        except Exception as e:
            return CreateCustomer(customer=None, message=f"Error: {str(e)}", success=False)

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(String)
    success = Boolean()

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, input):
        created = []
        errors = []
        
        for customer_data in input:
            try:
                if Customer.objects.filter(email=customer_data.email).exists():
                    errors.append(f"Customer {customer_data.name}: Email already exists")
                    continue
                
                if customer_data.phone and not re.match(r'^\+?1?[-\.\s]?\(?([0-9]{3})\)?[-\.\s]?([0-9]{3})[-\.\s]?([0-9]{4})$', customer_data.phone):
                    errors.append(f"Customer {customer_data.name}: Invalid phone format")
                    continue

                customer = Customer.objects.create(
                    name=customer_data.name,
                    email=customer_data.email,
                    phone=customer_data.phone or ""
                )
                created.append(customer)
            except Exception as e:
                errors.append(f"Customer {customer_data.name}: {str(e)}")
        
        return BulkCreateCustomers(
            customers=created,
            errors=errors,
            success=len(created) > 0
        )

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = String()

    @classmethod
    def mutate(cls, root, info, input):
        if input.price <= 0:
            raise ValidationError("Price must be positive")
        if input.stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock
        )
        return CreateProduct(product=product, message="Product created successfully")

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = String()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
            products = Product.objects.filter(id__in=input.product_ids)
            
            if not products.exists():
                raise ValidationError("No valid products found")
            if len(products) != len(input.product_ids):
                raise ValidationError("Some product IDs are invalid")

            total_amount = sum(p.price for p in products)
            
            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount
            )
            order.products.set(products)
            
            return CreateOrder(order=order, message="Order created successfully")
        except Customer.DoesNotExist:
            raise ValidationError("Customer not found")
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Error: {str(e)}")

# ✅ UPDATED QUERY CLASS WITH FILTERS
class Query(ObjectType):
    hello = String()
    
    def resolve_hello(root, info):
        return "Hello, GraphQL!"

    # ✅ FILTERED QUERIES WITH CONNECTION FIELDS
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

# Mutation
class Mutation(ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()