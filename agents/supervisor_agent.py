from typing import Dict, List, Any
import logging
from .spec_agent import SpecAgent
from .matchmaker_agent import MatchmakerAgent
from datetime import datetime
import os
import pathlib
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .tools.markdown_tool import MarkdownTool
import json

class SupervisorAgent:
    def __init__(self):
        self.spec_agent = SpecAgent()
        self.matchmaker_agent = MatchmakerAgent()
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM with fallback
        try:
            self.llm = ChatOpenAI(temperature=0.3)
        except Exception as e:
            self.logger.warning(f"Failed to initialize OpenAI: {e}")
            self.logger.info("Falling back to local Ollama model")
            self.llm = Ollama(model="llama2", temperature=0.3)
        
        # Define the supervisor prompt
        self.supervisor_prompt = PromptTemplate(
            input_variables=["order_specs", "matches"],
            template="""
            As a Supply Chain Supervisor, analyze the following order specifications and matching results:
            
            Order Specifications:
            {order_specs}
            
            Matching Results:
            {matches}
            
            Provide a brief analysis including:
            1. Whether the matches are satisfactory
            2. Any potential risks or concerns
            3. Recommendations for proceeding
            
            Keep the response concise and business-focused.
            """
        )
        
        # Create the analysis chain
        self.analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.supervisor_prompt
        )

        # Initialize tools
        self.tools = {
            "markdown": MarkdownTool()
        }

    def analyze_matches(self, specs: Dict[str, Any], matches: List[Dict[str, Any]]) -> str:
        """Analyze matches using LLM"""
        try:
            analysis = self.analysis_chain.run(
                order_specs=str(specs),
                matches=str(matches)
            )
            return analysis
        except Exception as e:
            self.logger.error(f"LLM analysis failed: {str(e)}")
            return "Analysis unavailable due to error"

    def process_order(self, order_text: str, inventory_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a single order text through the entire pipeline with AI analysis
        """
        try:
            # Extract specifications using SpecAgent
            specs = self.spec_agent.process_rfq(order_text)
            
            # Find matches using MatchmakerAgent
            matches = self.matchmaker_agent.compare_inventory(inventory_data, specs)
            
            # Get AI analysis
            ai_analysis = self.analyze_matches(specs, matches)
            
            return {
                "order_specifications": specs,
                "matching_results": matches,
                "ai_analysis": ai_analysis,
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
        """Format the results using the markdown tool"""
        return self.tools["markdown"].run(results)

    def process_multiple_orders(self, orders_text: str, inventory_data: List[Dict[str, Any]]) -> Dict[str, List]:
        """
        Process multiple orders from a text file
        Returns both raw and formatted results
        """
        try:
            # Get all orders at once as JSON array
            orders = self.spec_agent.process_multiple_rfqs(orders_text)
            
            raw_results = []
            formatted_results = []
            
            for i, order in enumerate(orders, 1):
                self.logger.info(f"Processing order #{i}")
                try:
                    matches = self.matchmaker_agent.compare_inventory(inventory_data, order)
                    result = {
                        "order_specifications": order,
                        "matching_results": matches,
                        "processed_at": datetime.now().isoformat(),
                        "status": "success"
                    }
                    raw_results.append(result)
                    formatted_results.append(self.format_results(result))
                except Exception as e:
                    self.logger.error(f"Error processing order #{i}: {str(e)}")
                    formatted_results.append(f"Error processing order #{i}: {str(e)}")
                
            return {
                "raw": raw_results,
                "formatted": formatted_results
            }
        except Exception as e:
            self.logger.error(f"Error processing multiple orders: {str(e)}")
            return {
                "raw": [],
                "formatted": [f"Error processing orders: {str(e)}"]
            }

    def save_results(self, results: Dict[str, List], output_dir: str = "/home/avi/docs/supply-ai/output") -> Dict[str, str]:
        """Save results to markdown and JSON files"""
        pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_file = os.path.join(output_dir, f"{timestamp}_order_analysis.md")
        json_file = os.path.join(output_dir, f"{timestamp}_order_specs.json")
        
        # Write markdown results
        with open(md_file, "w") as f:
            for i, result in enumerate(results["formatted"], 1):
                if i > 1:
                    f.write("\n\n---\n\n")
                f.write(result)

        # Save raw specifications
        if results["raw"]:
            specs = [r["order_specifications"] for r in results["raw"]]
            with open(json_file, "w") as f:
                json.dump(specs, f, indent=2)
            self.logger.info(f"Specifications saved to: {json_file}")
        else:
            json_file = None
            self.logger.warning("No raw specifications to save")
        
        self.logger.info(f"Results saved to: {md_file}")
        return {"markdown": md_file, "json": json_file}


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
    
    # Save results to files
    output_files = supervisor.save_results(results)
    
    # Print results location
    print(f"\nResults have been saved to: {output_files['markdown']}")
    if output_files['json']:
        print(f"Specifications saved to: {output_files['json']}")
