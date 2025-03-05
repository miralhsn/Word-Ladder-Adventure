from typing import Set, Dict
from pathlib import Path
from collections import defaultdict

class DictionaryHandler:
    def __init__(self, dictionary_path: str = None):
        self.dictionary: Set[str] = set()
        self.words_by_length: Dict[int, Set[str]] = defaultdict(set)
        self.transformation_cache: Dict[str, Set[str]] = {}
        self.dictionary_path = dictionary_path or str(Path(__file__).parent.parent / 'resources' / 'dictionary.txt')
        self.load_dictionary()
    
    def load_dictionary(self) -> None:
        """Load words from dictionary file."""
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                for word in f:
                    word = word.strip().lower()
                    if word:
                        self.dictionary.add(word)
                        self.words_by_length[len(word)].add(word)
        except FileNotFoundError:
            print("Dictionary file not found. Running with minimal word set.")
            # Fallback to a small built-in dictionary for testing
            minimal_words = {
                "cat", "bat", "hat", "hot", "dot", "dog",
                "big", "bag", "bug", "hug",
                "stone", "store", "score", "scare", "spare", "spade", "space", "peace", "place", "plane", "money"
            }
            for word in minimal_words:
                self.dictionary.add(word)
                self.words_by_length[len(word)].add(word)
    
    def is_valid_word(self, word: str) -> bool:
        """Check if a word exists in the dictionary."""
        return word.lower() in self.dictionary
    
    def get_words_of_length(self, length: int) -> Set[str]:
        """Get all words of specified length."""
        return self.words_by_length[length]
    
    def get_word_count(self) -> int:
        """Get total number of words in dictionary."""
        return len(self.dictionary)
    
    def get_length_distribution(self) -> Dict[int, int]:
        """Get distribution of word lengths."""
        return {length: len(words) for length, words in self.words_by_length.items()}
    
    def get_valid_transformations(self, word: str) -> Set[str]:
        """Get all valid one-letter transformations of a word."""
        if word in self.transformation_cache:
            return self.transformation_cache[word]
        
        transformations = set()
        word_len = len(word)
        possible_words = self.words_by_length[word_len]
        
        for i in range(word_len):
            pattern = word[:i] + '*' + word[i+1:]
            for other_word in possible_words:
                if other_word != word:
                    if other_word[:i] + '*' + other_word[i+1:] == pattern:
                        transformations.add(other_word)
        
        self.transformation_cache[word] = transformations
        return transformations 