from abc import ABC , abstractmethod
from typing import Dict , Any


class HtmlContract(ABC):
    @abstractmethod
    def render (self , snapshot:Dict[str , Any])-> str :
        pass