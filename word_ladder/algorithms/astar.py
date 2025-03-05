from typing import List
from .search_base import SearchAlgorithm
import heapq

class AStarSearch(SearchAlgorithm):
    def find_path(self, start: str, target: str) -> List[str]:
        """A* Search using f(n) = g(n) + h(n) for optimal pathfinding."""
        if len(start) != len(target):
            return []
        
        # Priority queue: (f_score, g_score, word)
        open_set = [(self.f(0, start, target), 0, start)]
        closed = set()
        came_from = {start: None}
        g_scores = {start: 0}
        
        while open_set:
            _, g_score, current = heapq.heappop(open_set)
            
            if current == target:
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            
            if current in closed:
                continue
            
            closed.add(current)
            
            # Explore neighbors
            for neighbor in self.word_graph[current]:
                if neighbor in closed:
                    continue
                
                tentative_g = self.g(g_score + 1)
                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    came_from[neighbor] = current
                    g_scores[neighbor] = tentative_g
                    f_score = self.f(tentative_g, neighbor, target)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))
        
        return [] 