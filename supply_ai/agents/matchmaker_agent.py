from supply_ai.tools.database_tool import DatabaseTool
import logging

class MatchmakerAgent:
    def __init__(self):
        self.db_tool = DatabaseTool()
        self.logger = logging.getLogger(__name__)
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the database"""
        try:
            self.db_tool.initialize_database()
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Database initialization failed: {str(e)}")
            raise

    def add_supplier(self, supplier_data: Dict[str, Any]) -> int:
        """Add a new supplier to the database"""
        try:
            supplier_id = self.db_tool.add_supplier(supplier_data)
            self.logger.info(f"Supplier added successfully with ID: {supplier_id}")
            return supplier_id
        except Exception as e:
            self.logger.error(f"Failed to add supplier: {str(e)}")
            raise

    def find_suppliers(self, specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find matching suppliers based on specifications"""
        try:
            self.logger.info("Searching for matching suppliers")
            results = self.db_tool.find_suppliers(specs)
            self.logger.info(f"Found {len(results)} matching suppliers")
            return results
        except Exception as e:
            self.logger.error(f"Supplier search failed: {str(e)}")
            raise
