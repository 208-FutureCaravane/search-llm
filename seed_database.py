"""
Seed the search_llm.db database with comprehensive fake data for testing the LLM system.
This script generates realistic restaurant, menu, dish, and ingredient data.
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

class DatabaseSeeder:
    def __init__(self, db_path='search_llm.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def clear_existing_data(self):
        """Clear existing data to start fresh"""
        tables = ['ingredient', '_PromotionDishes', 'promotions', 'reviews', 'loyalty_transactions', 
                 'loyalty_cards', 'payments', 'order_items', 'orders', 'reservations', 'tables', 
                 'dishes', 'menu_categories', 'menus', 'addresses', 'restaurants', 'users']
        
        for table in tables:
            try:
                self.cursor.execute(f"DELETE FROM {table}")
                print(f"✅ Cleared {table}")
            except Exception as e:
                print(f"⚠️  Could not clear {table}: {e}")
        self.conn.commit()
    
    def seed_restaurants(self):
        """Create diverse restaurants with different cuisines"""
        restaurants_data = [
            {
                'name': 'Pizza Palace', 
                'description': 'Authentic Italian pizzeria with wood-fired ovens and fresh ingredients',
                'phone': '023-456-789',
                'email': 'info@pizzapalace.dz',
                'operating_hours': json.dumps({
                    'monday': '11:00-23:00', 'tuesday': '11:00-23:00', 'wednesday': '11:00-23:00',
                    'thursday': '11:00-23:00', 'friday': '11:00-00:00', 'saturday': '11:00-00:00',
                    'sunday': '12:00-22:00'
                })
            },
            {
                'name': 'Burger Heaven',
                'description': 'Premium burgers made with locally sourced beef and artisan buns',
                'phone': '023-567-890',
                'email': 'contact@burgerheaven.dz',
                'operating_hours': json.dumps({
                    'monday': '12:00-22:00', 'tuesday': '12:00-22:00', 'wednesday': '12:00-22:00',
                    'thursday': '12:00-22:00', 'friday': '12:00-23:00', 'saturday': '12:00-23:00',
                    'sunday': '12:00-21:00'
                })
            },
            {
                'name': 'Sushi Zen',
                'description': 'Traditional Japanese sushi bar with fresh fish flown in daily',
                'phone': '023-678-901',
                'email': 'hello@sushizen.dz',
                'operating_hours': json.dumps({
                    'tuesday': '18:00-23:00', 'wednesday': '18:00-23:00', 'thursday': '18:00-23:00',
                    'friday': '18:00-00:00', 'saturday': '18:00-00:00', 'sunday': '18:00-22:00'
                })
            },
            {
                'name': 'Pasta Corner',
                'description': 'Homemade pasta with traditional Italian recipes and modern twists',
                'phone': '023-789-012',
                'email': 'info@pastacorner.dz',
                'operating_hours': json.dumps({
                    'monday': '11:30-22:30', 'tuesday': '11:30-22:30', 'wednesday': '11:30-22:30',
                    'thursday': '11:30-22:30', 'friday': '11:30-23:30', 'saturday': '11:30-23:30',
                    'sunday': '12:00-22:00'
                })
            },
            {
                'name': 'Spice Route',
                'description': 'Authentic Indian and Pakistani cuisine with aromatic spices and tandoor specialties',
                'phone': '023-890-123',
                'email': 'orders@spiceroute.dz',
                'operating_hours': json.dumps({
                    'monday': '12:00-22:00', 'tuesday': '12:00-22:00', 'wednesday': '12:00-22:00',
                    'thursday': '12:00-22:00', 'friday': '12:00-23:00', 'saturday': '12:00-23:00',
                    'sunday': '12:00-22:00'
                })
            },
            {
                'name': 'Mediterranean Breeze',
                'description': 'Fresh Mediterranean dishes with olive oil, herbs, and grilled specialties',
                'phone': '023-901-234',
                'email': 'info@medbreeze.dz',
                'operating_hours': json.dumps({
                    'monday': '10:00-22:00', 'tuesday': '10:00-22:00', 'wednesday': '10:00-22:00',
                    'thursday': '10:00-22:00', 'friday': '10:00-23:00', 'saturday': '10:00-23:00',
                    'sunday': '10:00-21:00'
                })
            }
        ]
        
        restaurant_ids = []
        for restaurant in restaurants_data:
            self.cursor.execute("""
                INSERT INTO restaurants (name, description, phone, email, operatingHours, isActive, createdAt, updatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (restaurant['name'], restaurant['description'], restaurant['phone'], 
                  restaurant['email'], restaurant['operating_hours'], True, datetime.now(), datetime.now()))
            restaurant_ids.append(self.cursor.lastrowid)
        
        self.conn.commit()
        print(f"✅ Created {len(restaurant_ids)} restaurants")
        return restaurant_ids
    
    def seed_menus_and_categories(self, restaurant_ids):
        """Create menus and categories for each restaurant"""
        menu_data = {
            'Pizza Palace': ['Pizzas', 'Appetizers', 'Salads', 'Desserts', 'Beverages'],
            'Burger Heaven': ['Burgers', 'Sides', 'Shakes', 'Salads', 'Desserts'],
            'Sushi Zen': ['Nigiri', 'Sashimi', 'Maki Rolls', 'Appetizers', 'Soups'],
            'Pasta Corner': ['Pasta', 'Risotto', 'Appetizers', 'Salads', 'Desserts'],
            'Spice Route': ['Curries', 'Tandoor', 'Rice Dishes', 'Bread', 'Appetizers'],
            'Mediterranean Breeze': ['Grilled Items', 'Mezze', 'Salads', 'Seafood', 'Desserts']
        }
        
        # Get restaurant names to match with categories
        self.cursor.execute("SELECT id, name FROM restaurants")
        restaurants = dict(self.cursor.fetchall())
        
        menu_category_ids = {}
        
        for restaurant_id, restaurant_name in restaurants.items():
            # Create main menu for restaurant
            self.cursor.execute("""
                INSERT INTO menus (restaurantId, name, description, isActive, displayOrder, createdAt, updatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (restaurant_id, f"{restaurant_name} Menu", f"Main menu for {restaurant_name}", 
                  True, 0, datetime.now(), datetime.now()))
            menu_id = self.cursor.lastrowid
            
            # Create categories for this menu
            categories = menu_data.get(restaurant_name, ['Main Dishes', 'Appetizers', 'Desserts'])
            menu_category_ids[restaurant_id] = []
            
            for i, category_name in enumerate(categories):
                self.cursor.execute("""
                    INSERT INTO menu_categories (menuId, name, description, isActive, displayOrder, createdAt, updatedAt)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (menu_id, category_name, f"{category_name} from {restaurant_name}", 
                      True, i, datetime.now(), datetime.now()))
                menu_category_ids[restaurant_id].append(self.cursor.lastrowid)
        
        self.conn.commit()
        total_categories = sum(len(cats) for cats in menu_category_ids.values())
        print(f"✅ Created menus and {total_categories} categories")
        return menu_category_ids
    
    def seed_dishes(self, menu_category_ids):
        """Create diverse dishes for each category"""
        dishes_data = {
            'Pizzas': [
                {'name': 'Margherita Pizza', 'description': 'Classic pizza with tomato sauce, mozzarella, and fresh basil', 'price': 1200},
                {'name': 'Pepperoni Pizza', 'description': 'Spicy pepperoni with mozzarella cheese and tomato sauce', 'price': 1400},
                {'name': 'Quattro Stagioni', 'description': 'Four seasons pizza with mushrooms, artichokes, olives, and ham', 'price': 1600},
                {'name': 'Vegetarian Supreme', 'description': 'Bell peppers, mushrooms, onions, tomatoes, and olives', 'price': 1350},
                {'name': 'Meat Lovers', 'description': 'Pepperoni, sausage, ham, and ground beef', 'price': 1800},
            ],
            'Burgers': [
                {'name': 'Classic Cheeseburger', 'description': 'Beef patty with cheddar cheese, lettuce, tomato, and special sauce', 'price': 900},
                {'name': 'BBQ Bacon Burger', 'description': 'Beef patty with crispy bacon, BBQ sauce, and onion rings', 'price': 1100},
                {'name': 'Mushroom Swiss Burger', 'description': 'Beef patty with sautéed mushrooms and Swiss cheese', 'price': 1050},
                {'name': 'Chicken Avocado Burger', 'description': 'Grilled chicken breast with avocado, lettuce, and mayo', 'price': 950},
                {'name': 'Veggie Burger', 'description': 'Plant-based patty with fresh vegetables and tahini sauce', 'price': 850},
            ],
            'Nigiri': [
                {'name': 'Salmon Nigiri', 'description': 'Fresh Atlantic salmon over seasoned sushi rice', 'price': 350},
                {'name': 'Tuna Nigiri', 'description': 'Premium bluefin tuna over sushi rice', 'price': 400},
                {'name': 'Shrimp Nigiri', 'description': 'Cooked shrimp over seasoned rice', 'price': 300},
                {'name': 'Eel Nigiri', 'description': 'Grilled eel with sweet glaze over sushi rice', 'price': 380},
                {'name': 'Sea Bass Nigiri', 'description': 'Fresh sea bass with a touch of yuzu', 'price': 360},
            ],
            'Pasta': [
                {'name': 'Spaghetti Carbonara', 'description': 'Classic carbonara with eggs, pancetta, and parmesan', 'price': 1300},
                {'name': 'Penne Arrabbiata', 'description': 'Spicy tomato sauce with garlic and red peppers', 'price': 1100},
                {'name': 'Fettuccine Alfredo', 'description': 'Creamy alfredo sauce with parmesan cheese', 'price': 1200},
                {'name': 'Lasagna Bolognese', 'description': 'Layers of pasta with meat sauce and béchamel', 'price': 1450},
                {'name': 'Seafood Linguine', 'description': 'Mixed seafood in white wine and garlic sauce', 'price': 1600},
            ],
            'Curries': [
                {'name': 'Chicken Tikka Masala', 'description': 'Tender chicken in creamy tomato curry sauce', 'price': 1400},
                {'name': 'Lamb Biryani', 'description': 'Aromatic basmati rice with spiced lamb', 'price': 1600},
                {'name': 'Butter Chicken', 'description': 'Mild chicken curry in rich tomato cream sauce', 'price': 1350},
                {'name': 'Vegetable Korma', 'description': 'Mixed vegetables in coconut curry sauce', 'price': 1200},
                {'name': 'Beef Vindaloo', 'description': 'Spicy beef curry with potatoes and vinegar', 'price': 1500},
            ],
            'Grilled Items': [
                {'name': 'Grilled Sea Bass', 'description': 'Fresh sea bass with lemon and herbs', 'price': 1800},
                {'name': 'Lamb Souvlaki', 'description': 'Grilled lamb skewers with tzatziki sauce', 'price': 1600},
                {'name': 'Grilled Halloumi', 'description': 'Grilled Cypriot cheese with olive oil', 'price': 900},
                {'name': 'Chicken Gyros', 'description': 'Marinated chicken with pita and vegetables', 'price': 1200},
                {'name': 'Mixed Grill Platter', 'description': 'Assorted grilled meats and vegetables', 'price': 2200},
            ]
        }
        
        # Get all categories with their restaurant info
        self.cursor.execute("""
            SELECT mc.id, mc.name, r.name as restaurant_name 
            FROM menu_categories mc 
            JOIN menus m ON mc.menuId = m.id 
            JOIN restaurants r ON m.restaurantId = r.id
        """)
        categories = self.cursor.fetchall()
        
        dish_ids = []
        
        for category_id, category_name, restaurant_name in categories:
            # Get appropriate dishes for this category
            if category_name in dishes_data:
                dishes = dishes_data[category_name]
            else:
                # Create generic dishes for categories not specifically defined
                dishes = [
                    {'name': f'{category_name} Special', 'description': f'House special {category_name.lower()} dish', 'price': random.randint(800, 1500)},
                    {'name': f'Classic {category_name}', 'description': f'Traditional {category_name.lower()} preparation', 'price': random.randint(700, 1300)},
                ]
            
            for dish in dishes:
                # Add some price variation
                price_variation = random.uniform(0.9, 1.1)  # ±10% variation
                adjusted_price = int(dish['price'] * price_variation)
                
                self.cursor.execute("""
                    INSERT INTO dishes (categoryId, name, description, price, isAvailable, quantity, preparationTime, popularity, displayOrder, createdAt, updatedAt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (category_id, dish['name'], dish['description'], adjusted_price, True, 
                      random.randint(5, 50), random.randint(10, 45), random.uniform(0, 5), 
                      random.randint(0, 10), datetime.now(), datetime.now()))
                dish_ids.append(self.cursor.lastrowid)
        
        self.conn.commit()
        print(f"✅ Created {len(dish_ids)} dishes")
        return dish_ids
    
    def seed_ingredients(self, dish_ids):
        """Create ingredient data for dishes"""
        # Common ingredients by cuisine type
        ingredient_sets = {
            'pizza': ['mozzarella cheese', 'tomato sauce', 'flour', 'olive oil', 'basil', 'oregano', 'pepperoni', 'mushrooms'],
            'burger': ['beef patty', 'bun', 'lettuce', 'tomato', 'onion', 'cheese', 'bacon', 'pickles', 'mayo'],
            'sushi': ['rice', 'nori', 'salmon', 'tuna', 'wasabi', 'soy sauce', 'ginger', 'cucumber'],
            'pasta': ['pasta', 'tomato sauce', 'parmesan cheese', 'garlic', 'olive oil', 'basil', 'ground beef', 'cream'],
            'indian': ['chicken', 'basmati rice', 'curry powder', 'turmeric', 'garam masala', 'coconut milk', 'onion', 'garlic'],
            'mediterranean': ['olive oil', 'lemon', 'garlic', 'herbs', 'feta cheese', 'tomato', 'cucumber', 'olives']
        }
        
        # Get dish information to determine cuisine type
        self.cursor.execute("""
            SELECT d.id, d.name, r.name as restaurant_name 
            FROM dishes d 
            JOIN menu_categories mc ON d.categoryId = mc.id 
            JOIN menus m ON mc.menuId = m.id 
            JOIN restaurants r ON m.restaurantId = r.id
        """)
        dishes_info = self.cursor.fetchall()
        
        ingredient_count = 0
        
        for dish_id, dish_name, restaurant_name in dishes_info:
            # Determine cuisine type based on restaurant
            if 'Pizza' in restaurant_name:
                ingredients = ingredient_sets['pizza']
            elif 'Burger' in restaurant_name:
                ingredients = ingredient_sets['burger']
            elif 'Sushi' in restaurant_name:
                ingredients = ingredient_sets['sushi']
            elif 'Pasta' in restaurant_name:
                ingredients = ingredient_sets['pasta']
            elif 'Spice' in restaurant_name:
                ingredients = ingredient_sets['indian']
            elif 'Mediterranean' in restaurant_name:
                ingredients = ingredient_sets['mediterranean']
            else:
                ingredients = ['salt', 'pepper', 'oil', 'herbs']
            
            # Add 3-6 random ingredients per dish
            num_ingredients = random.randint(3, 6)
            selected_ingredients = random.sample(ingredients, min(num_ingredients, len(ingredients)))
            
            for ingredient_name in selected_ingredients:
                quantity = random.uniform(0.1, 3.0)  # Random quantity
                self.cursor.execute("""
                    INSERT INTO ingredient (dishId, quantity)
                    VALUES (?, ?)
                """, (dish_id, quantity))
                ingredient_count += 1
        
        self.conn.commit()
        print(f"✅ Created {ingredient_count} ingredient relationships")
    
    def seed_users(self):
        """Create some test users"""
        users_data = [
            {'email': 'john.doe@email.com', 'phone': 555000001, 'firstName': 'John', 'lastName': 'Doe', 'role': 'CLIENT'},
            {'email': 'jane.smith@email.com', 'phone': 555000002, 'firstName': 'Jane', 'lastName': 'Smith', 'role': 'CLIENT'},
            {'email': 'chef.mario@pizzapalace.dz', 'phone': 555000003, 'firstName': 'Mario', 'lastName': 'Rossi', 'role': 'CHEF'},
            {'email': 'manager@burgerheaven.dz', 'phone': 555000004, 'firstName': 'Sarah', 'lastName': 'Johnson', 'role': 'MANAGER'},
            {'email': 'admin@system.dz', 'phone': 555000005, 'firstName': 'Admin', 'lastName': 'User', 'role': 'ADMIN'},
        ]
        
        user_ids = []
        for user in users_data:
            self.cursor.execute("""
                INSERT INTO users (email, phone, firstName, lastName, role, password, isActive, createdAt, updatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user['email'], user['phone'], user['firstName'], user['lastName'], 
                  user['role'], 'hashed_password', True, datetime.now(), datetime.now()))
            user_ids.append(self.cursor.lastrowid)
        
        self.conn.commit()
        print(f"✅ Created {len(user_ids)} users")
        return user_ids
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    print("🌱 Starting database seeding...")
    print("=" * 50)
    
    try:
        # Install faker if not available
        import faker
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "faker"])
        import faker
    
    seeder = DatabaseSeeder()
    
    # Clear existing data
    print("🧹 Clearing existing data...")
    seeder.clear_existing_data()
    
    # Seed all data
    restaurant_ids = seeder.seed_restaurants()
    menu_category_ids = seeder.seed_menus_and_categories(restaurant_ids)
    dish_ids = seeder.seed_dishes(menu_category_ids)
    seeder.seed_ingredients(dish_ids)
    user_ids = seeder.seed_users()
    
    seeder.close()
    
    print("\n" + "=" * 50)
    print("🎉 Database seeding completed successfully!")
    print(f"📊 Summary:")
    print(f"   - {len(restaurant_ids)} restaurants")
    print(f"   - {sum(len(cats) for cats in menu_category_ids.values())} menu categories")
    print(f"   - {len(dish_ids)} dishes")
    print(f"   - {len(user_ids)} users")
    print(f"\n🔥 Your database is now ready for LLM testing!")

if __name__ == "__main__":
    main()