from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from products.models import Product, Category
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Adds fake products to the database linked to the first user'

    def handle(self, *args, **options):
        # Get the first user (farmer)
        try:
            user = User.objects.filter(role='farmer').first()
            if not user:
                self.stdout.write(self.style.ERROR('No farmer users found in the database'))
                return
            self.stdout.write(self.style.SUCCESS(f'Using farmer: {user.first_name} {user.last_name} ({user.email})'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No users found in the database'))
            return

        # Create categories if they don't exist
        categories = [
            'Vegetables',
            'Fruits',
            'Dairy',
            'Meat',
            'Grains',
            'Herbs',
            'Nuts',
            'Honey',
            'Eggs',
            'Seafood'
        ]

        created_categories = []
        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            created_categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Using existing category: {category_name}'))

        # Product data
        vegetable_products = [
            ('Fresh Tomatoes', 'Juicy, ripe tomatoes freshly harvested from our farm.', Decimal('2.99'), 50),
            ('Organic Carrots', 'Sweet and crunchy organic carrots, perfect for salads or cooking.', Decimal('1.99'), 100),
            ('Green Lettuce', 'Crisp and fresh green lettuce, ideal for salads and sandwiches.', Decimal('1.49'), 30),
            ('Bell Peppers', 'Colorful bell peppers, great for stir-fries or stuffing.', Decimal('3.49'), 40),
            ('Spinach Bunch', 'Nutrient-rich spinach leaves, perfect for salads or cooking.', Decimal('2.49'), 25),
        ]

        fruit_products = [
            ('Organic Apples', 'Sweet and crisp organic apples, perfect for snacking.', Decimal('4.99'), 75),
            ('Fresh Strawberries', 'Juicy and sweet strawberries, freshly picked.', Decimal('3.99'), 30),
            ('Ripe Bananas', 'Perfectly ripe bananas, great for smoothies or baking.', Decimal('1.99'), 100),
            ('Juicy Oranges', 'Sweet and juicy oranges, packed with vitamin C.', Decimal('5.99'), 60),
            ('Fresh Blueberries', 'Plump and sweet blueberries, perfect for desserts or snacking.', Decimal('4.49'), 40),
        ]

        dairy_products = [
            ('Farm Fresh Milk', 'Creamy, fresh milk from grass-fed cows.', Decimal('3.99'), 20),
            ('Organic Cheese', 'Artisanal cheese made from organic milk.', Decimal('6.99'), 15),
            ('Fresh Butter', 'Creamy butter made from fresh cream.', Decimal('4.99'), 25),
            ('Organic Yogurt', 'Probiotic-rich yogurt made from organic milk.', Decimal('3.49'), 30),
        ]

        meat_products = [
            ('Grass-Fed Beef', 'Premium beef from grass-fed, free-range cattle.', Decimal('12.99'), 10),
            ('Free-Range Chicken', 'Tender chicken raised on a free-range farm.', Decimal('8.99'), 15),
            ('Organic Pork', 'Flavorful pork from organically raised pigs.', Decimal('9.99'), 12),
        ]

        grain_products = [
            ('Organic Wheat Flour', 'Finely milled organic wheat flour, perfect for baking.', Decimal('4.99'), 50),
            ('Brown Rice', 'Nutritious brown rice, a healthy alternative to white rice.', Decimal('5.99'), 40),
            ('Quinoa', 'Protein-rich quinoa, a versatile grain for various dishes.', Decimal('7.99'), 30),
        ]

        # Create products
        with transaction.atomic():
            # Map categories to product lists
            category_products = {
                'Vegetables': vegetable_products,
                'Fruits': fruit_products,
                'Dairy': dairy_products,
                'Meat': meat_products,
                'Grains': grain_products,
            }

            products_created = 0

            for category_name, products_data in category_products.items():
                category = Category.objects.get(name=category_name)

                for name, description, price, stock in products_data:
                    product = Product(
                        name=name,
                        description=description,
                        price=price,
                        category=category,
                        stock_quantity=stock,
                        status='available',
                        farmer=user
                    )
                    product.save()
                    products_created += 1
                    self.stdout.write(self.style.SUCCESS(f'Created product: {name} (${price})'))

            self.stdout.write(self.style.SUCCESS(f'Successfully created {products_created} products'))
