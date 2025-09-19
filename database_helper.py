"""
Database helper class for the search-llm project.
This module provides easy access to the restaurant database for LLM queries.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Dish:
    """Represents a dish from the database"""
    id: int
    name: str
    description: str
    price: float
    category: str
    restaurant: str
    restaurant_id: int
    category_id: int

@dataclass
class Restaurant:
    """Represents a restaurant from the database"""
    id: int
    name: str
    description: str
    phone: str
    email: str

class RestaurantDatabase:
    """
    Helper class to interact with the restaurant database for LLM queries.
    This class provides methods to search for dishes based on various criteria.
    """
    
    def __init__(self, db_path: str = 'search_llm.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
    
    def get_all_dishes(self) -> List[Dish]:
        """Get all dishes with their restaurant and category information"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                d.id, d.name, d.description, d.price,
                mc.name as category, mc.id as category_id,
                r.name as restaurant, r.id as restaurant_id
            FROM dishes d
            JOIN menu_categories mc ON d.categoryId = mc.id
            JOIN menus m ON mc.menuId = m.id
            JOIN restaurants r ON m.restaurantId = r.id
            WHERE d.isAvailable = TRUE
            ORDER BY d.name
        """)
        
        dishes = []
        for row in cursor.fetchall():
            dishes.append(Dish(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                price=row['price'],
                category=row['category'],
                restaurant=row['restaurant'],
                restaurant_id=row['restaurant_id'],
                category_id=row['category_id']
            ))
        
        return dishes
    
    def search_dishes_by_name(self, query: str) -> List[int]:
        """
        Search for dishes by name or description.
        Returns list of dish IDs.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT d.id
            FROM dishes d
            WHERE d.isAvailable = TRUE 
            AND (d.name LIKE ? OR d.description LIKE ?)
            ORDER BY d.id
        """, (f'%{query}%', f'%{query}%'))
        
        return [row[0] for row in cursor.fetchall()]
    
    def search_dishes_by_category(self, category: str) -> List[int]:
        """
        Search for dishes by category name.
        Returns list of dish IDs.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT d.id
            FROM dishes d
            JOIN menu_categories mc ON d.categoryId = mc.id
            WHERE d.isAvailable = TRUE 
            AND mc.name LIKE ?
            ORDER BY d.id
        """, (f'%{category}%',))
        
        return [row[0] for row in cursor.fetchall()]
    
    def search_dishes_by_price_range(self, min_price: Optional[float] = None, 
                                   max_price: Optional[float] = None) -> List[int]:
        """
        Search for dishes by price range.
        Returns list of dish IDs.
        """
        cursor = self.conn.cursor()
        
        conditions = ["d.isAvailable = TRUE"]
        params = []
        
        if min_price is not None:
            conditions.append("d.price >= ?")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("d.price <= ?")
            params.append(max_price)
        
        query = f"""
            SELECT DISTINCT d.id
            FROM dishes d
            WHERE {' AND '.join(conditions)}
            ORDER BY d.price
        """
        
        cursor.execute(query, params)
        return [row[0] for row in cursor.fetchall()]
    
    def search_dishes_by_restaurant(self, restaurant_query: str) -> List[int]:
        """
        Search for dishes by restaurant name or description.
        Returns list of dish IDs.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT d.id
            FROM dishes d
            JOIN menu_categories mc ON d.categoryId = mc.id
            JOIN menus m ON mc.menuId = m.id
            JOIN restaurants r ON m.restaurantId = r.id
            WHERE d.isAvailable = TRUE 
            AND (r.name LIKE ? OR r.description LIKE ?)
            ORDER BY d.id
        """, (f'%{restaurant_query}%', f'%{restaurant_query}%'))
        
        return [row[0] for row in cursor.fetchall()]
    
    def get_dishes_by_ids(self, dish_ids: List[int]) -> List[Dish]:
        """Get detailed information for specific dish IDs"""
        if not dish_ids:
            return []
        
        cursor = self.conn.cursor()
        placeholders = ','.join(['?' for _ in dish_ids])
        
        cursor.execute(f"""
            SELECT 
                d.id, d.name, d.description, d.price,
                mc.name as category, mc.id as category_id,
                r.name as restaurant, r.id as restaurant_id
            FROM dishes d
            JOIN menu_categories mc ON d.categoryId = mc.id
            JOIN menus m ON mc.menuId = m.id
            JOIN restaurants r ON m.restaurantId = r.id
            WHERE d.id IN ({placeholders})
            ORDER BY d.price
        """, dish_ids)
        
        dishes = []
        for row in cursor.fetchall():
            dishes.append(Dish(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                price=row['price'],
                category=row['category'],
                restaurant=row['restaurant'],
                restaurant_id=row['restaurant_id'],
                category_id=row['category_id']
            ))
        
        return dishes
    
    def get_all_restaurants(self) -> List[Restaurant]:
        """Get all restaurants"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, description, phone, email
            FROM restaurants
            WHERE isActive = TRUE
            ORDER BY name
        """)
        
        restaurants = []
        for row in cursor.fetchall():
            restaurants.append(Restaurant(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                phone=row['phone'],
                email=row['email'] or ''
            ))
        
        return restaurants
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all menu categories"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT mc.id, mc.name, r.name as restaurant
            FROM menu_categories mc
            JOIN menus m ON mc.menuId = m.id
            JOIN restaurants r ON m.restaurantId = r.id
            WHERE mc.isActive = TRUE
            ORDER BY r.name, mc.name
        """)
        
        return [{'id': row[0], 'name': row[1], 'restaurant': row[2]} 
                for row in cursor.fetchall()]
    
    def complex_search(self, 
                      name_query: Optional[str] = None,
                      category: Optional[str] = None,
                      restaurant: Optional[str] = None,
                      min_price: Optional[float] = None,
                      max_price: Optional[float] = None) -> List[int]:
        """
        Perform a complex search combining multiple criteria.
        Returns list of dish IDs that match all specified criteria.
        """
        cursor = self.conn.cursor()
        
        conditions = ["d.isAvailable = TRUE"]
        params = []
        
        if name_query:
            conditions.append("(d.name LIKE ? OR d.description LIKE ?)")
            params.extend([f'%{name_query}%', f'%{name_query}%'])
        
        if category:
            conditions.append("mc.name LIKE ?")
            params.append(f'%{category}%')
        
        if restaurant:
            conditions.append("(r.name LIKE ? OR r.description LIKE ?)")
            params.extend([f'%{restaurant}%', f'%{restaurant}%'])
        
        if min_price is not None:
            conditions.append("d.price >= ?")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("d.price <= ?")
            params.append(max_price)
        
        query = f"""
            SELECT DISTINCT d.id
            FROM dishes d
            JOIN menu_categories mc ON d.categoryId = mc.id
            JOIN menus m ON mc.menuId = m.id
            JOIN restaurants r ON m.restaurantId = r.id
            WHERE {' AND '.join(conditions)}
            ORDER BY d.price
        """
        
        cursor.execute(query, params)
        return [row[0] for row in cursor.fetchall()]
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get statistics about the database"""
        cursor = self.conn.cursor()
        
        stats = {}
        tables = ['restaurants', 'dishes', 'menu_categories', 'users']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Example usage and test functions
def test_database_helper():
    """Test the database helper functions"""
    with RestaurantDatabase() as db:
        print("🧪 Testing RestaurantDatabase helper class")
        print("=" * 50)
        
        # Test basic stats
        stats = db.get_database_stats()
        print(f"📊 Database contains:")
        for table, count in stats.items():
            print(f"   {table}: {count} records")
        
        # Test search functions
        print(f"\n🔍 Search Examples:")
        
        # Search for pizza
        pizza_ids = db.search_dishes_by_name("pizza")
        print(f"Pizza dishes: {pizza_ids}")
        
        # Search by price range
        affordable_ids = db.search_dishes_by_price_range(max_price=1000)
        print(f"Affordable dishes (< 1000 DZD): {affordable_ids[:5]}...")
        
        # Complex search
        italian_affordable = db.complex_search(
            restaurant="pizza",
            max_price=1500
        )
        print(f"Affordable pizza restaurant dishes: {italian_affordable}")
        
        # Get dish details
        if pizza_ids:
            dish_details = db.get_dishes_by_ids(pizza_ids[:2])
            print(f"\n📋 Sample dish details:")
            for dish in dish_details:
                print(f"   {dish.name} - {dish.price} DZD ({dish.restaurant})")

if __name__ == "__main__":
    test_database_helper()