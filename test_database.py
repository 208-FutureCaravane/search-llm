"""
Test the seeded database with sample queries to verify data for LLM testing.
This script demonstrates various queries the LLM might need to perform.
"""

import sqlite3
import json
from typing import List, Dict, Any

class DatabaseTester:
    def __init__(self, db_path='search_llm.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # This allows column access by name
    
    def test_basic_data(self):
        """Test that basic data is present"""
        cursor = self.conn.cursor()
        
        # Count records in each table
        tables = ['restaurants', 'menus', 'menu_categories', 'dishes', 'ingredient', 'users']
        
        print("📊 Database Statistics:")
        print("-" * 30)
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:15}: {count:3} records")
    
    def test_dish_queries(self):
        """Test dish-related queries that the LLM might need"""
        cursor = self.conn.cursor()
        
        print("\n🍕 Sample Dish Queries:")
        print("-" * 30)
        
        # Query 1: Find pizza dishes
        print("1. Find all pizza dishes:")
        cursor.execute("""
            SELECT d.id, d.name, d.description, d.price, r.name as restaurant
            FROM dishes d
            JOIN menu_categories mc ON d.categoryId = mc.id
            JOIN menus m ON mc.menuId = m.id  
            JOIN restaurants r ON m.restaurantId = r.id
            WHERE d.name LIKE '%Pizza%' OR mc.name LIKE '%Pizza%'
            ORDER BY d.price
        """)
        
        pizza_dishes = cursor.fetchall()
        for dish in pizza_dishes[:3]:  # Show first 3
            print(f"   ID: {dish['id']}, {dish['name']} - {dish['price']} DZD ({dish['restaurant']})")
        
        # Query 2: Find dishes under 1000 DZD
        print("\n2. Affordable dishes (under 1000 DZD):")
        cursor.execute("""
            SELECT d.id, d.name, d.price, r.name as restaurant
            FROM dishes d
            JOIN menu_categories mc ON d.categoryId = mc.id
            JOIN menus m ON mc.menuId = m.id
            JOIN restaurants r ON m.restaurantId = r.id
            WHERE d.price < 1000
            ORDER BY d.price
            LIMIT 5
        """)
        
        affordable_dishes = cursor.fetchall()
        for dish in affordable_dishes:
            print(f"   ID: {dish['id']}, {dish['name']} - {dish['price']} DZD ({dish['restaurant']})")
        
        # Query 3: Find dishes by restaurant type
        print("\n3. Italian restaurant dishes:")
        cursor.execute("""
            SELECT d.id, d.name, d.description, d.price
            FROM dishes d
            JOIN menu_categories mc ON d.categoryId = mc.id
            JOIN menus m ON mc.menuId = m.id
            JOIN restaurants r ON m.restaurantId = r.id
            WHERE r.name LIKE '%Pizza%' OR r.name LIKE '%Pasta%'
            ORDER BY d.price
            LIMIT 5
        """)
        
        italian_dishes = cursor.fetchall()
        for dish in italian_dishes:
            print(f"   ID: {dish['id']}, {dish['name']} - {dish['price']} DZD")
    
    def test_ingredient_queries(self):
        """Test ingredient-based filtering"""
        cursor = self.conn.cursor()
        
        print("\n🥬 Ingredient-Based Queries:")
        print("-" * 30)
        
        # Find dishes with specific ingredients (this would need ingredient names in the schema)
        # For now, we'll show the structure
        print("1. Sample ingredient relationships:")
        cursor.execute("""
            SELECT d.id, d.name, i.quantity, r.name as restaurant
            FROM dishes d
            JOIN ingredient i ON d.id = i.dishId
            JOIN menu_categories mc ON d.categoryId = mc.id
            JOIN menus m ON mc.menuId = m.id
            JOIN restaurants r ON m.restaurantId = r.id
            LIMIT 5
        """)
        
        ingredients = cursor.fetchall()
        for item in ingredients:
            print(f"   Dish ID: {item['id']}, {item['name']} has {item['quantity']:.1f} units of ingredient ({item['restaurant']})")
    
    def test_price_range_queries(self):
        """Test price-based filtering"""
        cursor = self.conn.cursor()
        
        print("\n💰 Price Range Queries:")
        print("-" * 30)
        
        price_ranges = [
            ("Budget (< 800 DZD)", "d.price < 800"),
            ("Mid-range (800-1300 DZD)", "d.price BETWEEN 800 AND 1300"),
            ("Premium (> 1300 DZD)", "d.price > 1300")
        ]
        
        for label, condition in price_ranges:
            cursor.execute(f"""
                SELECT COUNT(*) as count, MIN(d.price) as min_price, MAX(d.price) as max_price
                FROM dishes d
                WHERE {condition}
            """)
            
            result = cursor.fetchone()
            print(f"   {label}: {result['count']} dishes (range: {result['min_price']}-{result['max_price']} DZD)")
    
    def test_restaurant_queries(self):
        """Test restaurant-based queries"""
        cursor = self.conn.cursor()
        
        print("\n🏪 Restaurant Information:")
        print("-" * 30)
        
        cursor.execute("""
            SELECT r.id, r.name, r.description, COUNT(d.id) as dish_count
            FROM restaurants r
            LEFT JOIN menus m ON r.id = m.restaurantId
            LEFT JOIN menu_categories mc ON m.id = mc.menuId
            LEFT JOIN dishes d ON mc.id = d.categoryId
            GROUP BY r.id, r.name, r.description
            ORDER BY dish_count DESC
        """)
        
        restaurants = cursor.fetchall()
        for restaurant in restaurants:
            print(f"   ID: {restaurant['id']}, {restaurant['name']} - {restaurant['dish_count']} dishes")
            print(f"      {restaurant['description'][:60]}...")
    
    def generate_sample_llm_queries(self):
        """Generate sample queries that the LLM should be able to handle"""
        cursor = self.conn.cursor()
        
        print("\n🤖 Sample LLM Test Cases:")
        print("-" * 40)
        
        test_cases = [
            {
                'user_query': "I want to eat pizza",
                'sql_query': """
                    SELECT DISTINCT d.id
                    FROM dishes d
                    JOIN menu_categories mc ON d.categoryId = mc.id
                    WHERE d.name LIKE '%Pizza%' OR mc.name LIKE '%Pizza%'
                """,
                'description': "Should return dish IDs for pizza items"
            },
            {
                'user_query': "Show me pasta dishes under 1200 DZD",
                'sql_query': """
                    SELECT DISTINCT d.id
                    FROM dishes d
                    JOIN menu_categories mc ON d.categoryId = mc.id
                    WHERE (d.name LIKE '%Pasta%' OR mc.name LIKE '%Pasta%') 
                    AND d.price < 1200
                """,
                'description': "Should return affordable pasta dish IDs"
            },
            {
                'user_query': "Find dishes from Italian restaurants",
                'sql_query': """
                    SELECT DISTINCT d.id
                    FROM dishes d
                    JOIN menu_categories mc ON d.categoryId = mc.id
                    JOIN menus m ON mc.menuId = m.id
                    JOIN restaurants r ON m.restaurantId = r.id
                    WHERE r.name LIKE '%Pizza%' OR r.name LIKE '%Pasta%'
                """,
                'description': "Should return dish IDs from Italian-style restaurants"
            },
            {
                'user_query': "Show me expensive dishes over 1500 DZD",
                'sql_query': """
                    SELECT DISTINCT d.id
                    FROM dishes d
                    WHERE d.price > 1500
                """,
                'description': "Should return premium dish IDs"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. User Query: '{test_case['user_query']}'")
            print(f"   Expected: {test_case['description']}")
            
            cursor.execute(test_case['sql_query'])
            results = cursor.fetchall()
            dish_ids = [row[0] for row in results]
            
            print(f"   Result: {dish_ids[:10]}{'...' if len(dish_ids) > 10 else ''}")  # Show first 10 IDs
            print(f"   Total: {len(dish_ids)} dishes found")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    print("🧪 Testing Seeded Database")
    print("=" * 50)
    
    tester = DatabaseTester()
    
    tester.test_basic_data()
    tester.test_dish_queries()
    tester.test_ingredient_queries()
    tester.test_price_range_queries()
    tester.test_restaurant_queries()
    tester.generate_sample_llm_queries()
    
    tester.close()
    
    print("\n" + "=" * 50)
    print("✅ Database testing completed!")
    print("🚀 Your database is ready for LLM integration in model.ipynb")

if __name__ == "__main__":
    main()