# intel_providers/base.py

from abc import ABC, abstractmethod

class IntelProvider(ABC):
    """
    Base interface for all intelligence providers.
    """

    @abstractmethod
    def analyze(self, file_path: str) -> dict:
        """
        Analyze the given file and return intelligence data.
        """
        pass
