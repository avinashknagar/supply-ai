from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser
from supply_ai.config.config import Config
import logging

class LLMTool:
    def __init__(self):
        self.config = Config()
        self.llm_config = self.config.get_config()["llm_config"]
        self.llm = Ollama(
            model=self.llm_config["model"],
            temperature=self.llm_config["temperature"]
        )
        self.parser = JsonOutputParser()
        self.logger = logging.getLogger(__name__)

    def process_text(self, prompt: str) -> Dict[str, Any]:
        """Process text using the LLM"""
        try:
            self.logger.info(f"Processing prompt: {prompt[:100]}...")
            response = self.llm(prompt)
            parsed_response = self.parser.parse(response)
            self.logger.info("LLM processing completed successfully")
            return parsed_response
        except Exception as e:
            self.logger.error(f"LLM processing failed: {str(e)}")
            raise

    def get_llm_config(self) -> Dict[str, Any]:
        """Get current LLM configuration"""
        return self.llm_config
