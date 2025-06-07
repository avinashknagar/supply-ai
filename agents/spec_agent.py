from tools.llm_tool import LLMTool
import logging
from typing import Dict, Any

class SpecAgent:
    def __init__(self):
        self.llm_tool = LLMTool()
        self.logger = logging.getLogger(__name__)

    def process_rfq(self, text: str) -> Dict[str, Any]:
        """Process RFQ text and extract specifications"""
        try:
            self.logger.info("Processing RFQ text")
            prompt = f"""Based on the input text, create a JSON object with extracted information.
            ONLY return a valid JSON object, no additional text.
            If a field is not found, use null or empty list.
            Required format:
            {{
                "material": string,
                "purity": float,
                "quantity": string,
                "technical_requirements": string[]
            }}

            Input text:
            {text}"""
            return self.llm_tool.process_text(prompt)
        except Exception as e:
            self.logger.error(f"RFQ processing failed: {str(e)}")
            raise
            
    def process_multiple_rfqs(self, orders_text: str) -> Dict[str, Any]:
        """Process multiple RFQs from a single text"""
        try:
            self.logger.info("Processing multiple RFQs")
            prompt = f"""Extract all orders from the input text into a JSON array.
            ONLY return a valid JSON array, no additional text.
            Each order should follow this format:
            {{
                "order_id": number,
                "material": string,
                "purity": float,
                "quantity": string,
                "technical_requirements": string[]
            }}

            Input text:
            {orders_text}"""
            return self.llm_tool.process_text(prompt)
        except Exception as e:
            self.logger.error(f"Multiple RFQ processing failed: {str(e)}")
            raise
