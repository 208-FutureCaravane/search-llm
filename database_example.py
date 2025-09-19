"""
SQLite Database Connection Example
This shows how to use the created SQLite database with raw SQL queries.
Since Prisma client generation had issues, we can use direct SQLite connections.
"""

import sqlite3
from datetime import datetime
import json

class SearchLLMDB:
    def __init__(self, db_path='search_llm.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def create_user(self, email, phone, first_name, last_name, password, role='CLIENT'):
        """Create a new user in the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (email, phone, firstName, lastName, role, password, isActive, createdAt, updatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (email, phone, first_name, last_name, role, password, True, datetime.now(), datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def create_restaurant(self, name, description, phone, email, operating_hours):
        """Create a new restaurant"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Convert operating hours dict to JSON string for storage
            operating_hours_json = json.dumps(operating_hours) if isinstance(operating_hours, dict) else operating_hours
            cursor.execute("""
                INSERT INTO restaurants (name, description, phone, email, operatingHours, isActive, createdAt, updatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, description, phone, email, operating_hours_json, True, datetime.now(), datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_users(self):
        """Get all users from the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            columns = [description[0] for description in cursor.description]
            results = cursor.fetchall()
            return [dict(zip(columns, row)) for row in results]
    
    def get_all_restaurants(self):
        """Get all restaurants from the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM restaurants")
            columns = [description[0] for description in cursor.description]
            results = cursor.fetchall()
            return [dict(zip(columns, row)) for row in results]

# Example usage
if __name__ == "__main__":
    db = SearchLLMDB()
    
    print("🎉 SQLite Database is ready!")
    print("=" * 50)
    
    # Example: Create a user
    try:
        user_id = db.create_user(
            email="test@example.com",
            phone=1234567890,
            first_name="John",
            last_name="Doe",
            password="hashed_password_here",
            role="CLIENT"
        )
        print(f"✅ Created user with ID: {user_id}")
    except Exception as e:
        print(f"User might already exist or error: {e}")
    
    # Example: Create a restaurant
    try:
        restaurant_id = db.create_restaurant(
            name="Test Restaurant",
            description="A great place to eat",
            phone="555-0123",
            email="restaurant@example.com",
            operating_hours={"monday": "9:00-21:00", "tuesday": "9:00-21:00"}
        )
        print(f"✅ Created restaurant with ID: {restaurant_id}")
    except Exception as e:
        print(f"Restaurant might already exist or error: {e}")
    
    # Show current data
    users = db.get_all_users()
    restaurants = db.get_all_restaurants()
    
    print(f"\n📊 Database contains:")
    print(f"  - {len(users)} user(s)")
    print(f"  - {len(restaurants)} restaurant(s)")
    
    print("\n🔧 You can now:")
    print("  - Use this class to interact with the database")
    print("  - Add more methods for your specific needs")
    print("  - Use any SQLite client to view/edit data")
    print(f"  - Database file: {db.db_path}")