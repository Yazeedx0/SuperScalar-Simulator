from typing import List, Dict, Optional

class PipelineStage:
    """
    Represents a stage in a superscalar pipeline processor.
    
    Attributes:
        name (str): Name identifier for the pipeline stage
        instructions (List[Optional[int]]): List of instruction IDs currently in this stage
        details (List[Dict]): Associated metadata for each instruction
        stalled (bool): Flag indicating if the stage is stalled
    """
    
    def __init__(self, name: str, width: int = 2) -> None:
        """
        Initialize a new pipeline stage.
        
        Args:
            name (str): Name identifier for the stage
            width (int): Number of parallel instructions that can be processed (default: 2)
        """
        self.name = name
        self.instructions: List[Optional[int]] = [None] * width
        self.details: List[Dict] = [{}] * width
        self.stalled = False
