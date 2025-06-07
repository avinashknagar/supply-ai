from typing import Dict, List, Any
import logging
from .spec_agent import SpecAgent
from .matchmaker_agent import MatchmakerAgent
from datetime import datetime
import os
import pathlib

class SupervisorAgent:
    def __init__(self):
        self.spec_agent = SpecAgent()
        self.matchmaker_agent = MatchmakerAgent()
        self.logger = logging.getLogger(__name__)

    def process_order(self, order_text: str, inventory_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a single order text through the entire pipeline
        """
        try:
            # Extract specifications using SpecAgent
            specs = self.spec_agent.process_rfq(order_text)
            
            # Find matches using MatchmakerAgent
            matches = self.matchmaker_agent.compare_inventory(inventory_data, specs)
            
            return {
                "order_specifications": specs,
                "matching_results": matches,
                "processed_at": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"Order processing failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }

    def format_results(self, results: Dict[str, Any]) -> str:
        """
        Format the results into a human-readable format
        """
        if results["status"] == "error":
            return f"Error processing order: {results['error']}"

        output = []
        output.append("=== Order Analysis Report ===")
        output.append("\nOrder Specifications:")
        specs = results["order_specifications"]
        output.append(f"- Material: {specs.get('material', 'N/A')}")
        output.append(f"- Purity: {specs.get('purity', 'N/A')}")
        output.append(f"- Quantity: {specs.get('quantity', 'N/A')}")
        output.append(f"- Technical Requirements: {specs.get('technical_requirements', 'N/A')}")

        output.append("\nMatching Results:")
        matches = results["matching_results"]
        if not matches:
            output.append("No matches found in inventory.")
        else:
            for idx, match in enumerate(matches[:3], 1):  # Show top 3 matches
                output.append(f"\nMatch #{idx} (Score: {match['match_score']})")
                item = match['inventory_item']
                output.append(f"- Material: {item.get('material', 'N/A')}")
                output.append(f"- Purity: {item.get('purity', 'N/A')}")
                output.append(f"- Quantity: {item.get('quantity', 'N/A')}")
                output.append(f"- Technical Requirements: {item.get('technical_requirements', 'N/A')}")
                output.append("Comments:")
                for comment in match['comments']:
                    output.append(f"  * {comment}")

        output.append(f"\nProcessed at: {results['processed_at']}")
        return "\n".join(output)

    def process_multiple_orders(self, orders_text: str, inventory_data: List[Dict[str, Any]]) -> List[str]:
        """
        Process multiple orders from a text file
        """
        # Split the text into individual orders
        orders = orders_text.strip().split("Order")
        orders = [o.strip() for o in orders if o.strip()]
        
        all_results = []
        for i, order in enumerate(orders, 1):
            self.logger.info(f"Processing order #{i}")
            results = self.process_order(order, inventory_data)
            formatted_result = self.format_results(results)
            all_results.append(formatted_result)
            
        return all_results

    def save_results(self, results: List[str], output_dir: str = "/home/avi/docs/supply-ai/output") -> str:
        """
        Save results to a file in the output directory
        """
        # Ensure output directory exists
        pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"order_analysis_{timestamp}.txt")
        
        # Write results to file
        with open(output_file, "w") as f:
            f.write("\n\n" + "="*50 + "\n\n".join(results) + "\n" + "="*50)
        
        self.logger.info(f"Results saved to: {output_file}")
        return output_file


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Sample inventory data
    sample_inventory = [
        {
            "material": "Hydrochloric Acid",
            "purity": "37%",
            "quantity": "1000 kg/month",
            "technical_requirements": ["Industrial Grade"]
        },
        # ... more inventory items ...
    ]
    
    # Create supervisor agent
    supervisor = SupervisorAgent()
    
    # Read orders from file
    with open("/home/avi/docs/supply-ai/input/order.txt", "r") as f:
        orders_text = f.read()
    
    # Process all orders
    results = supervisor.process_multiple_orders(orders_text, sample_inventory)
    
    # Save results to file
    output_file = supervisor.save_results(results)
    
    # Print results location
    print(f"\nResults have been saved to: {output_file}")
