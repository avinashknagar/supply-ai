import streamlit as st
from agents.supervisor_agent import SupervisorAgent
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def load_inventory(inventory_path="/home/avi/docs/supply-ai/input/inventory.json"):
    """Load inventory data from JSON file"""
    try:
        with open(inventory_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return sample inventory if file doesn't exist
        return [
            {
                "material": "Hydrochloric Acid",
                "purity": "37%",
                "quantity": "1000 kg/month",
                "technical_requirements": ["Industrial Grade"]
            },
            {
                "material": "Sulfuric Acid",
                "purity": "98%",
                "quantity": "2000 kg/month",
                "technical_requirements": ["Pharma Grade", "Low Water Content"]
            }
        ]

def cli_mode():
    """Run in command-line mode"""
    logger.info("Starting order processing in CLI mode")
    
    # Initialize supervisor agent
    supervisor = SupervisorAgent()
    
    # Load inventory
    inventory_data = load_inventory()
    
    try:
        # Read orders from file
        with open("/home/avi/docs/supply-ai/input/order.txt", "r") as f:
            orders_text = f.read()
        
        # Process orders
        results = supervisor.process_multiple_orders(orders_text, inventory_data)
        
        # Save results
        output_file = supervisor.save_results(results)
        
        print(f"\nProcessing complete!")
        print(f"Results have been saved in Markdown format to: {output_file}")
        print("\nSummary of processed orders (Markdown preview):")
        for i, result in enumerate(results, 1):
            print(f"\n{'='*60}")
            print(result)
            print(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Error processing orders: {str(e)}")
        print(f"Error: {str(e)}")

def main():
    """Main entry point that handles both Streamlit and CLI modes"""
    try:
        # Check if script is running under Streamlit
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx():
            st.title("Supply AI Order Processing")
            # ... your existing Streamlit code ...
        else:
            cli_mode()
    except:
        # If not running in Streamlit or if there's an error importing,
        # default to CLI mode
        cli_mode()

if __name__ == "__main__":
    main()
