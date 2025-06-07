from abc import ABC, abstractmethod
from typing import Any

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the tool name"""
        pass
    
    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the tool's primary function"""
        pass
