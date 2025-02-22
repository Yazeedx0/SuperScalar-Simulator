from typing import List, Dict, Optional

class PipelineStage:
    def __init__(self, name: str, width: int = 2):
        self.name = name
        self.instructions: List[Optional[int]] = [None] * width  
        self.details: List[Dict] = [{}] * width
        self.stalled = False
