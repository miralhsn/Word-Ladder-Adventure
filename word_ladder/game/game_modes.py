from enum import Enum, auto
from typing import List
from dataclasses import dataclass
import random
from word_ladder.game.dictionary_handler import DictionaryHandler

class DifficultyLevel(Enum): #enum used for better readability
    BEGINNER = auto()
    ADVANCED = auto()
    CHALLENGE = auto()

# datclass handles various types of difficulty levels
@dataclass
class Challenge:
    start_word: str
    target_word: str
    max_moves: int
    banned_words: List[str] = None
    restricted_letters: List[str] = None

class GameMode:
    # classic game mode for users choosing classic challenge option. 
    DEFAULT_CHALLENGES = {
        DifficultyLevel.BEGINNER: [
            Challenge("cat", "dog", 4),
            Challenge("big", "hug", 3),
            Challenge("hat", "rat", 4),
            Challenge("sit", "dog", 4),
            Challenge("pen", "ink", 3),
            Challenge("mad", "joy", 4),
        ],
        DifficultyLevel.ADVANCED: [
            Challenge("word", "play", 5),
            Challenge("warm", "cold", 6),
            Challenge("peace", "place", 5),
            Challenge("sleep", "awake", 6),
            Challenge("light", "dark", 5),
            Challenge("happy", "angry", 6),
        ],
        DifficultyLevel.CHALLENGE: [
            Challenge("stone", "money", 7, banned_words=["store", "score"]),
            Challenge("peace", "place", 4, restricted_letters=["s", "t"]),
            Challenge("spare", "space", 5, banned_words=["spade"], restricted_letters=["t"]),
            Challenge("heart", "break", 6, banned_words=["heat", "beat"], restricted_letters=["s"]),
            Challenge("night", "light", 5, restricted_letters=["s", "p", "w"]),
            Challenge("water", "flame", 7, banned_words=["waste", "wave"], restricted_letters=["p"]),
        ]
    }

    def __init__(self, difficulty: DifficultyLevel, use_random: bool = False):
        self.difficulty = difficulty
        print(f"\nInitializing {difficulty.name} mode...")
        
        if not use_random:
            self.challenges = self.DEFAULT_CHALLENGES[difficulty]
            return

        self.dictionary = DictionaryHandler()
        self.challenges = self._create_random_challenges()

    def _create_random_challenges(self) -> List[Challenge]:
        """Create random challenges by picking words from dictionary based on the difficulty level the user chooses."""
        challenges = [] #stores list of challenges created 
        
        # checks the difficulty level
        if self.difficulty == DifficultyLevel.BEGINNER:
            #  word length between 3-4 letters
            for _ in range(6):
                length = random.randint(3, 4)
                words = list(self.dictionary.get_words_of_length(length)) #retrive words from dictionary
                if len(words) < 2: #skip if words are too short
                    continue
                start_word = random.choice(words)
                target_word = random.choice(words) # randomly selects two words from list
                while target_word == start_word:
                    target_word = random.choice(words)
                challenges.append(Challenge(start_word, target_word, 5))
                
        elif self.difficulty == DifficultyLevel.ADVANCED:
            # word length between 4-5 letters
            for _ in range(6):
                length = random.randint(4, 5)
                words = list(self.dictionary.get_words_of_length(length))
                if len(words) < 2:
                    continue
                start_word = random.choice(words)
                target_word = random.choice(words)
                while target_word == start_word:
                    target_word = random.choice(words)
                challenges.append(Challenge(start_word, target_word, 6))
                
        else:  
            # CHALLENGE
            # word length between 5-6 letter words with restrictions
            for _ in range(6):
                length = random.randint(5, 6)
                words = list(self.dictionary.get_words_of_length(length))
                if len(words) < 2:
                    continue
                start_word = random.choice(words)
                target_word = random.choice(words)
                while target_word == start_word:
                    target_word = random.choice(words)
                    
                # Add some random banned words
                banned = random.sample(words, min(2, len(words)-2)) if len(words) > 3 else None
                
                # Add some random restricted letters
                restricted = random.sample('abcdefghijklmnopqrstuvwxyz', 2)
                
                challenges.append(Challenge(
                    start_word, target_word, 7,
                    banned_words=banned,
                    restricted_letters=restricted
                ))
        
        # If we couldn't create enough random challenges, use defaults
        if len(challenges) < 3:
            return self.DEFAULT_CHALLENGES[self.difficulty]
            
        return challenges[:3]  # Return only first 3 challenges 