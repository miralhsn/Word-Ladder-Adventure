from typing import List, Optional, Type, Dict
from word_ladder.game.dictionary_handler import DictionaryHandler
from word_ladder.game.game_modes import GameMode, DifficultyLevel, Challenge
from word_ladder.algorithms.search_base import SearchAlgorithm
from word_ladder.algorithms.astar import AStarSearch
from word_ladder.algorithms.ucs import UniformCostSearch
from word_ladder.algorithms.bfs import BreadthFirstSearch
from word_ladder.game.high_score_handler import HighScoreHandler

class WordLadderGame:
    def __init__(self, dictionary_path: str = None):
        self.dictionary = DictionaryHandler(dictionary_path)
        self.current_mode: Optional[GameMode] = None
        self.current_challenge: Optional[Challenge] = None
        self.moves: List[str] = []
        self.hints_used: int = 0
        self.moves_made: int = 0
        self.current_challenge_index: int = 0
        self.available_algorithms = {
            'astar': AStarSearch,
            'ucs': UniformCostSearch,
            'bfs': BreadthFirstSearch
        }
        self.high_score_handler = HighScoreHandler()
        self.current_score = 0
        self.points_per_move = {
            DifficultyLevel.BEGINNER: 50,
            DifficultyLevel.ADVANCED: 75,
            DifficultyLevel.CHALLENGE: 100
        }
        self.wrong_move_penalty = {
            DifficultyLevel.BEGINNER: -25,
            DifficultyLevel.ADVANCED: -35,
            DifficultyLevel.CHALLENGE: -50
        }
    
    def start_game(self, difficulty: DifficultyLevel, use_random: bool = False) -> None:
        """Start a new game with specified difficulty."""
        self.current_mode = GameMode(difficulty, use_random)  # Pass use_random to GameMode
        self.current_challenge_index = 0
        self._start_challenge()
    
    def _start_challenge(self) -> None:
        """Start a new challenge."""
        if self.current_mode and self.current_challenge_index < len(self.current_mode.challenges):
            self.current_challenge = self.current_mode.challenges[self.current_challenge_index]
            self.moves = [self.current_challenge.start_word]
            self.hints_used = 0
            self.moves_made = 0
            self.current_score = 0  # Reset score for new challenge
    
    def next_challenge(self) -> bool:
        """Move to the next challenge. Returns True if there is a next challenge."""
        if not self.current_mode:
            return False
        
        self.current_challenge_index += 1
        if self.current_challenge_index < len(self.current_mode.challenges):
            self._start_challenge()
            return True
        return False

    def get_hint(self, algorithm_name: str = 'astar') -> Optional[str]:
        """Get next word suggestion using specified algorithm."""
        if not self.current_challenge or not self.moves:
            return None
            
        algorithm_class = self.available_algorithms.get(algorithm_name)
        if not algorithm_class:
            return None
            
        current_word = self.moves[-1]
        target_word = self.current_challenge.target_word
        
        # Create algorithm instance with current dictionary
        algorithm = algorithm_class(set(self.dictionary.dictionary))  # Convert to set explicitly
        
        # Find path from current word to target
        path = algorithm.find_path(current_word, target_word)
        
        # Return next word in path if found and valid
        if len(path) > 1:
            next_word = path[1]
            if self._is_valid_move(next_word):
                self.hints_used += 1
                self.current_score -= 25  # Apply hint penalty
                return next_word
        return None

    def get_score(self) -> int:
        """Get the current score."""
        return max(0, self.current_score)  # Never go below 0

    def update_high_score(self) -> bool:
        """Update high score if current score is higher. Returns True if new high score."""
        if not self.current_mode:
            return False
        
        current_score = self.get_score()
        if self.high_score_handler.update_high_score(self.current_mode.difficulty, current_score):
            print(f"\n🏆 New High Score for {self.current_mode.difficulty.name}: {current_score}!")
            return True
        return False

    def get_progress_info(self) -> dict:
        """Get current game progress information."""
        if not self.current_challenge or not self.current_mode:
            return {}
            
        current_score = self.get_score()
        high_score = self.high_score_handler.get_high_score(self.current_mode.difficulty)
        
        return {
            'challenge_number': self.current_challenge_index + 1,
            'total_challenges': len(self.current_mode.challenges),
            'moves_made': self.moves_made,
            'moves_left': max(0, self.current_challenge.max_moves - self.moves_made),
            'hints_used': self.hints_used,
            'current_score': current_score,
            'high_score': high_score
        }

    def make_move(self, word: str) -> bool:
        """Attempt to make a move in the game."""
        if not self.current_challenge:
            return False
            
        # Increment moves counter regardless of validity
        self.moves_made += 1
        
        # Check if we've exceeded max moves
        if self.moves_made > self.current_challenge.max_moves:
            return False
            
        if not self._is_valid_move(word):
            # Apply penalty for wrong move
            self.current_score += self.wrong_move_penalty[self.current_mode.difficulty]
            return False
            
        # Add points for correct move
        self.current_score += self.points_per_move[self.current_mode.difficulty]
        self.moves.append(word)
        
        # If challenge completed, add bonus points
        if self.is_complete():
            moves_left = self.current_challenge.max_moves - self.moves_made
            bonus = moves_left * self.points_per_move[self.current_mode.difficulty]
            self.current_score += bonus
        
        return True
    
    def _is_valid_move(self, word: str) -> bool:
        """Check if the move is valid according to game rules."""
        if not self.dictionary.is_valid_word(word):
            return False
            
        if not self.moves:
            return False
            
        if len(word) != len(self.moves[-1]):
            return False
            
        # Check if only one letter different
        differences = sum(1 for a, b in zip(word, self.moves[-1]) if a != b)
        if differences != 1:
            return False
            
        # Check challenge-specific rules
        if self.current_challenge.banned_words and word in self.current_challenge.banned_words:
            return False
            
        if self.current_challenge.restricted_letters:
            if any(letter in word for letter in self.current_challenge.restricted_letters):
                return False
        
        return True
    
    def is_complete(self) -> bool:
        """Check if the current challenge is complete."""
        return (self.current_challenge and self.moves and 
                self.moves[-1] == self.current_challenge.target_word) 