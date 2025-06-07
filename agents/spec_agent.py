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
            prompt = f"""Extract key information from the RFQ:
            {{
                "material": "chemical name",
                "purity": "percentage",
                "quantity": "kg/month",
                "technical_requirements": "list of requirements"
            }}
            Input: {text}"""
            return self.llm_tool.process_text(prompt)
        except Exception as e:
            self.logger.error(f"RFQ processing failed: {str(e)}")
            raise
