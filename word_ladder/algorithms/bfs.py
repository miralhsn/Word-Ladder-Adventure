from typing import List
from collections import deque
from .search_base import SearchAlgorithm

class BreadthFirstSearch(SearchAlgorithm):
    def find_path(self, start: str, target: str) -> List[str]:
        """BFS for layer-by-layer word exploration."""
        if len(start) != len(target):
            return []
        
        # Queue for BFS
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current, path = queue.popleft()
            
            if current == target:
                return path
            
            # Explore all neighbors at current depth
            for neighbor in self.word_graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path))
        
        return [] 