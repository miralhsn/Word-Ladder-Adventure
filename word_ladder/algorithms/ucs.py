from typing import List
from .search_base import SearchAlgorithm
import heapq

class UniformCostSearch(SearchAlgorithm):
    def find_path(self, start: str, target: str) -> List[str]:
        """UCS using only g(n) for systematic exploration."""
        if len(start) != len(target):
            return []
        
        # Priority queue: (cost, word)
        open_set = [(0, start)]
        closed = set()
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while open_set:
            current_cost, current = heapq.heappop(open_set)
            
            if current == target:
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            
            if current in closed:
                continue
            
            closed.add(current)
            
            # Explore neighbors with uniform cost
            for neighbor in self.word_graph[current]:
                if neighbor in closed:
                    continue
                
                new_cost = self.g(current_cost + 1)
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current
                    heapq.heappush(open_set, (new_cost, neighbor))
        
        return []  