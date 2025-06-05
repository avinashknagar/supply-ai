import sqlite3
from typing import List, Dict, Any
from supply_ai.config.config import Config

class DatabaseTool:
    def __init__(self):
        self.config = Config()
        self.config.ensure_directories()
        self.db_path = self.config.get_config()["db_path"]

    def initialize_database(self):
        """Initialize the suppliers database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                chemical TEXT NOT NULL,
                purity REAL NOT NULL,
                delivery_rating REAL NOT NULL,
                min_order REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def add_supplier(self, supplier_data: Dict[str, Any]) -> int:
        """Add a new supplier to the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO suppliers (name, chemical, purity, delivery_rating, min_order)
            VALUES (?, ?, ?, ?, ?)
        """, (
            supplier_data['name'],
            supplier_data['chemical'],
            supplier_data['purity'],
            supplier_data['delivery_rating'],
            supplier_data['min_order']
        ))
        supplier_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return supplier_id

    def find_suppliers(self, specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find suppliers matching the specifications"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, chemical, purity, delivery_rating, min_order,
            (1 - ABS(purity - ?)) * 0.6 + 
            (delivery_rating) * 0.4 AS score
            FROM suppliers
            WHERE chemical = ?
            ORDER BY score DESC
        """, (specs['purity'], specs['material']))
        results = cursor.fetchall()
        conn.close()
        return [{
            'name': row[0],
            'chemical': row[1],
            'purity': row[2],
            'delivery_rating': row[3],
            'min_order': row[4],
            'score': row[5]
        } for row in results]

    def _get_connection(self):
        """Get a database connection with proper error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            raise Exception(f"Database connection error: {str(e)}")
