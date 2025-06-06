"""
Pattern detection module for coin flip simulations.
Provides modular pattern detection classes for different coin flip patterns.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import math


class Pattern(ABC):
    """Abstract base class for pattern detection."""
    
    @abstractmethod
    def check_pattern(self, flips: List[int]) -> Tuple[bool, Optional[int]]:
        """
        Check if pattern is found in the flip sequence.
        
        Args:
            flips: List of coin flips (0=tails, 1=heads)
            
        Returns:
            Tuple of (pattern_found, position_of_pattern)
        """
        pass
    
    @abstractmethod
    def get_theoretical_ev(self) -> float:
        """Get theoretical expected value for this pattern."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of the pattern."""
        pass


class ConsecutivePattern(Pattern):
    """Base class for consecutive patterns (heads or tails)."""
    
    def __init__(self, length: int, target_value: int):
        """
        Initialize consecutive pattern.
        
        Args:
            length: Number of consecutive flips needed
            target_value: 0 for tails, 1 for heads
        """
        self.length = length
        self.target_value = target_value
        self.name = "heads" if target_value == 1 else "tails"
    
    def check_pattern(self, flips: List[int]) -> Tuple[bool, Optional[int]]:
        """Check for consecutive pattern in flip sequence."""
        if len(flips) < self.length:
            return False, None
        
        consecutive_count = 0
        for i, flip in enumerate(flips):
            if flip == self.target_value:
                consecutive_count += 1
                if consecutive_count >= self.length:
                    return True, i - self.length + 1
            else:
                consecutive_count = 0
        
        return False, None
    
    def get_theoretical_ev(self) -> float:
        """
        Calculate theoretical expected value for consecutive pattern.
        For n consecutive outcomes, EV = 2^(n+1) - 2
        """
        return 2**(self.length + 1) - 2
    
    def get_description(self) -> str:
        """Get description of the pattern."""
        return f"{self.length} consecutive {self.name}"


class ConsecutiveTails(ConsecutivePattern):
    """Pattern for consecutive tails."""
    
    def __init__(self, length: int):
        super().__init__(length, 0)


class ConsecutiveHeads(ConsecutivePattern):
    """Pattern for consecutive heads."""
    
    def __init__(self, length: int):
        super().__init__(length, 1)


class AlternatingPattern(Pattern):
    """Pattern for alternating heads and tails."""
    
    def __init__(self, length: int):
        """
        Initialize alternating pattern.
        
        Args:
            length: Number of alternating flips needed
        """
        self.length = length
    
    def check_pattern(self, flips: List[int]) -> Tuple[bool, Optional[int]]:
        """Check for alternating pattern in flip sequence."""
        if len(flips) < self.length:
            return False, None
        
        for i in range(len(flips) - self.length + 1):
            is_alternating = True
            for j in range(1, self.length):
                if flips[i + j] == flips[i + j - 1]:
                    is_alternating = False
                    break
            
            if is_alternating:
                return True, i
        
        return False, None
    
    def get_theoretical_ev(self) -> float:
        """
        Calculate theoretical expected value for alternating pattern.
        This is more complex and depends on the specific length.
        """
        # Simplified calculation - actual calculation is more complex
        return 2**self.length
    
    def get_description(self) -> str:
        """Get description of the pattern."""
        return f"{self.length} alternating flips"


class CustomPattern(Pattern):
    """Custom pattern defined by a specific sequence."""
    
    def __init__(self, sequence: List[int], description: str = ""):
        """
        Initialize custom pattern.
        
        Args:
            sequence: Specific sequence to match (0=tails, 1=heads)
            description: Human-readable description
        """
        self.sequence = sequence
        self.description = description or f"Custom sequence: {sequence}"
    
    def check_pattern(self, flips: List[int]) -> Tuple[bool, Optional[int]]:
        """Check for custom pattern in flip sequence."""
        if len(flips) < len(self.sequence):
            return False, None
        
        for i in range(len(flips) - len(self.sequence) + 1):
            if flips[i:i + len(self.sequence)] == self.sequence:
                return True, i
        
        return False, None
    
    def get_theoretical_ev(self) -> float:
        """
        Calculate theoretical expected value for custom pattern.
        For a specific sequence of length n, EV ≈ 2^n (simplified)
        """
        return 2**len(self.sequence)
    
    def get_description(self) -> str:
        """Get description of the pattern."""
        return self.description


# Predefined pattern configurations
PATTERN_CONFIGS = {
    "2_consecutive_tails": ConsecutiveTails(2),
    "2_consecutive_heads": ConsecutiveHeads(2),
    "3_consecutive_tails": ConsecutiveTails(3),
    "3_consecutive_heads": ConsecutiveHeads(3),
    "4_consecutive_tails": ConsecutiveTails(4),
    "4_consecutive_heads": ConsecutiveHeads(4),
    "3_alternating": AlternatingPattern(3),
    "4_alternating": AlternatingPattern(4),
    "heads_tails_heads": CustomPattern([1, 0, 1], "Heads-Tails-Heads"),
    "tails_heads_tails": CustomPattern([0, 1, 0], "Tails-Heads-Tails"),
}

