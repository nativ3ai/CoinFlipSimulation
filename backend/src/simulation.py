"""
Coin flip simulation module.
Handles individual coin flip sessions and pattern detection.
"""

import random
from typing import List, Optional, Dict, Any
from src.patterns import Pattern, PATTERN_CONFIGS


class CoinFlipSession:
    """Represents a single coin flip session."""
    
    def __init__(self, session_id: int, pattern: Pattern, max_flips: int = 10000):
        """
        Initialize a coin flip session.
        
        Args:
            session_id: Unique identifier for the session
            pattern: Pattern to detect
            max_flips: Maximum number of flips before stopping
        """
        self.session_id = session_id
        self.pattern = pattern
        self.max_flips = max_flips
        self.flips: List[int] = []
        self.completed = False
        self.pattern_found = False
        self.pattern_position: Optional[int] = None
        self.stopped_reason = ""
    
    def flip_coin(self) -> int:
        """Flip a coin and return result (0=tails, 1=heads)."""
        return random.randint(0, 1)
    
    def add_flip(self, flip_result: int) -> bool:
        """
        Add a flip result and check for pattern completion.
        
        Args:
            flip_result: Result of coin flip (0=tails, 1=heads)
            
        Returns:
            True if session should continue, False if completed
        """
        if self.completed:
            return False
        
        self.flips.append(flip_result)
        
        # Check for pattern
        pattern_found, position = self.pattern.check_pattern(self.flips)
        if pattern_found:
            self.pattern_found = True
            self.pattern_position = position
            self.completed = True
            self.stopped_reason = "pattern_found"
            return False
        
        # Check max flips limit
        if len(self.flips) >= self.max_flips:
            self.completed = True
            self.stopped_reason = "max_flips_reached"
            return False
        
        return True
    
    def run_until_completion(self) -> Dict[str, Any]:
        """
        Run the session until completion (pattern found or max flips).
        
        Returns:
            Dictionary with session results
        """
        while not self.completed:
            flip_result = self.flip_coin()
            self.add_flip(flip_result)
        
        return self.get_status()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current session status."""
        return {
            "session_id": self.session_id,
            "flips": self.flips.copy(),
            "flips_count": len(self.flips),
            "completed": self.completed,
            "pattern_found": self.pattern_found,
            "pattern_position": self.pattern_position,
            "stopped_reason": self.stopped_reason,
            "pattern_description": self.pattern.get_description()
        }


class CoinFlipSimulator:
    """Main simulator class for managing multiple sessions."""
    
    def __init__(self):
        """Initialize the simulator."""
        self.sessions: Dict[int, CoinFlipSession] = {}
        self.current_pattern: Optional[Pattern] = None
        self.num_sessions = 1000
        self.max_flips_per_session = 10000
        self.is_running = False
    
    def configure_simulation(self, pattern_name: str, num_sessions: int = 1000, 
                           max_flips_per_session: int = 10000) -> bool:
        """
        Configure the simulation parameters.
        
        Args:
            pattern_name: Name of pattern from PATTERN_CONFIGS
            num_sessions: Number of parallel sessions
            max_flips_per_session: Maximum flips per session
            
        Returns:
            True if configuration successful, False otherwise
        """
        if pattern_name not in PATTERN_CONFIGS:
            return False
        
        self.current_pattern = PATTERN_CONFIGS[pattern_name]
        self.num_sessions = num_sessions
        self.max_flips_per_session = max_flips_per_session
        return True
    
    def start_simulation(self) -> bool:
        """
        Start a new simulation with configured parameters.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.current_pattern is None:
            return False
        
        if self.is_running:
            return False
        
        # Clear previous sessions
        self.sessions.clear()
        
        # Create new sessions
        for i in range(self.num_sessions):
            session = CoinFlipSession(
                session_id=i,
                pattern=self.current_pattern,
                max_flips=self.max_flips_per_session
            )
            self.sessions[i] = session
        
        self.is_running = True
        return True
    
    def stop_simulation(self):
        """Stop the current simulation."""
        self.is_running = False
    
    def reset_simulation(self):
        """Reset all sessions and stop simulation."""
        self.sessions.clear()
        self.is_running = False
    
    def step_simulation(self) -> Dict[str, Any]:
        """
        Perform one step of simulation (one flip per active session).
        
        Returns:
            Dictionary with simulation status and updates
        """
        if not self.is_running:
            return {"status": "not_running", "updates": []}
        
        updates = []
        active_sessions = 0
        
        for session in self.sessions.values():
            if not session.completed:
                active_sessions += 1
                flip_result = session.flip_coin()
                should_continue = session.add_flip(flip_result)
                
                updates.append({
                    "session_id": session.session_id,
                    "flip_result": flip_result,
                    "flips_count": len(session.flips),
                    "completed": session.completed,
                    "pattern_found": session.pattern_found
                })
        
        # Stop simulation if no active sessions
        if active_sessions == 0:
            self.is_running = False
        
        return {
            "status": "running" if self.is_running else "completed",
            "active_sessions": active_sessions,
            "updates": updates
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calculate and return simulation statistics."""
        if not self.sessions:
            return {}
        
        total_sessions = len(self.sessions)
        completed_sessions = sum(1 for s in self.sessions.values() if s.completed)
        pattern_found_sessions = sum(1 for s in self.sessions.values() if s.pattern_found)
        
        # Calculate average flips for completed sessions
        completed_flips = [len(s.flips) for s in self.sessions.values() if s.completed]
        avg_flips = sum(completed_flips) / len(completed_flips) if completed_flips else 0
        
        # Calculate average flips for pattern-found sessions
        pattern_flips = [len(s.flips) for s in self.sessions.values() if s.pattern_found]
        avg_pattern_flips = sum(pattern_flips) / len(pattern_flips) if pattern_flips else 0
        
        # Theoretical expected value
        theoretical_ev = self.current_pattern.get_theoretical_ev() if self.current_pattern else 0
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "pattern_found_sessions": pattern_found_sessions,
            "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0,
            "pattern_success_rate": pattern_found_sessions / completed_sessions if completed_sessions > 0 else 0,
            "average_flips_all": avg_flips,
            "average_flips_pattern_found": avg_pattern_flips,
            "theoretical_ev": theoretical_ev,
            "actual_ev": avg_pattern_flips,
            "pattern_description": self.current_pattern.get_description() if self.current_pattern else "",
            "is_running": self.is_running
        }
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get status of all sessions."""
        return [session.get_status() for session in self.sessions.values()]
    
    def get_available_patterns(self) -> Dict[str, str]:
        """Get all available pattern configurations."""
        return {name: pattern.get_description() for name, pattern in PATTERN_CONFIGS.items()}


# Global simulator instance
simulator = CoinFlipSimulator()

