import os
import json
from typing import Dict
from word_ladder.game.game_modes import DifficultyLevel

class HighScoreHandler:
    def __init__(self):
        self.file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'high_scores.json')
        self._ensure_data_directory()
        self.high_scores = self._load_high_scores()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        directory = os.path.dirname(self.file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def _load_high_scores(self) -> Dict[str, int]:
        """Load high scores from file."""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    scores = json.load(f)
            else:
                scores = {}
            
            # Ensure all difficulty levels have a score
            for difficulty in DifficultyLevel:
                if difficulty.name not in scores:
                    scores[difficulty.name] = 0
            
            return scores
        except (json.JSONDecodeError, FileNotFoundError):
            return {difficulty.name: 0 for difficulty in DifficultyLevel}
    
    def _save_high_scores(self) -> None:
        """Save high scores to file immediately."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.high_scores, f)
        except Exception as e:
            print(f"Warning: Could not save high scores: {e}")
    
    def get_high_score(self, difficulty: DifficultyLevel) -> int:
        """Get high score for a difficulty level."""
        return self.high_scores.get(difficulty.name, 0)
    
    def update_high_score(self, difficulty: DifficultyLevel, score: int) -> bool:
        """Update high score if the new score is higher. Returns True if updated."""
        current_high_score = self.high_scores.get(difficulty.name, 0)
        if score > current_high_score:
            self.high_scores[difficulty.name] = score
            self._save_high_scores()  # Save immediately when new high score is set
            return True
        return False 