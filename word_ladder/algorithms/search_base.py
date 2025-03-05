from abc import ABC, abstractmethod
from typing import List, Set, Dict
from collections import defaultdict

class SearchAlgorithm(ABC):
    def __init__(self, dictionary: Set[str]):
        self.dictionary = dictionary
        self.word_graph = defaultdict(set)
        self._build_word_graph()
    
    def _build_word_graph(self) -> None:
        """Builds an adjacency list of valid word transformations."""
        words_by_length: Dict[int, Set[str]] = defaultdict(set)
        
        # Build sets of words by length
        for word in self.dictionary:
            words_by_length[len(word)].add(word)
        
        # Build graph only for words of same length
        for words in words_by_length.values():
            for word in words:
                for i in range(len(word)):
                    pattern = word[:i] + '*' + word[i+1:]
                    for other_word in words:
                        if other_word != word and other_word[:i] + '*' + other_word[i+1:] == pattern:
                            self.word_graph[word].add(other_word)
    
    def g(self, path_length: int) -> int:
        """Cost function g(n): Number of transformations from start."""
        return path_length
    
    def h(self, current: str, target: str) -> int:
        """Heuristic function h(n): Estimated transformations needed."""
        return sum(1 for a, b in zip(current, target) if a != b)
    
    def f(self, g_score: int, current: str, target: str) -> int:
        """Total cost function f(n) = g(n) + h(n)."""
        return g_score + self.h(current, target)
    
    @abstractmethod
    def find_path(self, start: str, target: str) -> List[str]:
        """Find path from start word to target word."""
        pass
    
    def get_neighbors(self, word: str) -> Set[str]:
        """Get all valid one-letter transformations of a word."""
        return self.word_graph[word] 