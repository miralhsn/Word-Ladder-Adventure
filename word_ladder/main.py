from word_ladder.game.word_ladder_game import WordLadderGame
from word_ladder.game.game_modes import DifficultyLevel, Challenge, GameMode
import sys
import os
from typing import List, Set
import networkx as nx
import string
import signal
import threading
import time

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("""
╔══════════════════════════════════════════════════════╗
║                Word Ladder Adventure                 ║
║          Transform words one letter at a time!       ║
╚══════════════════════════════════════════════════════╝
    """)

def print_help():
    print("""
Available Commands:
  move <word>  - Transform to a new word (e.g., 'move cat')
  hint        - Get a suggestion for the next move (-25 points)
  show        - Show current game progress
  restart     - Start the current challenge over
  next        - Move to next challenge (if available)
  quit        - Exit the game
    """)

def print_game_status(game: WordLadderGame):
    """Print current game status with visual enhancements."""
    info = game.get_progress_info()
    challenge = game.current_challenge
    
    print("\n" + "="*50)
    print(f"Challenge {info['challenge_number']}/{info['total_challenges']}")
    print(f"Difficulty: {game.current_mode.difficulty.name}")
    print("="*50)
    
    # Show word ladder
    print("\nWord Ladder:")
    for i, word in enumerate(game.moves):
        if i > 0:
            print("   ↓")
        print(f"  {word}")
    
    print("\nTarget Word:", challenge.target_word)
    print(f"Moves Left: {info['moves_left']}")
    print(f"Hints Used: {info['hints_used']}")
    
    if challenge.banned_words:
        print("Banned Words:", ", ".join(challenge.banned_words))
    if challenge.restricted_letters:
        print("Restricted Letters:", ", ".join(challenge.restricted_letters))
    
    print(f"\nCurrent Score: {info['current_score']}")
    print(f"High Score: {info['high_score']}")
    print("="*50)

def show_progress(message: str):
    """Show a simple progress indicator."""
    print(f"\r{message}...", end="", flush=True)

def user_create_custom_challenge(game: WordLadderGame) -> bool:
    """Allow users to create a custom word ladder challenge of their choice."""
    print("\nCreate Custom Challenge")
    print("======================")
    
    # give a start word of choice
    while True:
        start_word = input("Enter starting word: ").strip().lower()
        if not game.dictionary.is_valid_word(start_word):
            print("Invalid start word - does not exist in dictionary!")
            print("Try another word or press Enter to cancel")
            if not start_word:
                return False
        else:
            break
    
    # give a target word of choice 
    while True:
        target_word = input("Enter target word: ").strip().lower()
        if not game.dictionary.is_valid_word(target_word):
            print("Invalid target word - not in dictionary!")
            print("Try another word or press Enter to cancel")
            if not target_word:
                return False
        else:
            break
    
    # check the length of the words
    if len(start_word) != len(target_word):
        print(f"Error: Words must be the same length! ({len(start_word)} ≠ {len(target_word)})")
        return False
    
    # check whether path exists in the directory
    temp_challenge = Challenge(start_word, target_word, 10)  # Temporary max_moves
    game.current_challenge = temp_challenge
    game.moves = [start_word]
    
    # Simplified path check to avoid getting stuck
    print("\nChecking if path exists...")
    
    # Simple BFS to check path existence with timeout
    def check_path_exists(start, target, max_depth=10, timeout=5):
        print("Using simplified path finder...", end="", flush=True)
        start_time = time.time()
        
        # Quick check to see if words differ by just one letter
        differences = sum(1 for a, b in zip(start, target) if a != b)
        if differences == 1:
            print("\rPath exists! (direct transformation)        ")
            return [start, target]  # Direct path
            
        visited = set([start])
        queue = [(start, [start])]
        
        while queue and time.time() - start_time < timeout:
            current, path = queue.pop(0)
            
            # Get all possible next words by changing one letter at a time
            for i in range(len(current)):
                for letter in string.ascii_lowercase:
                    if letter != current[i]:
                        next_word = current[:i] + letter + current[i+1:]
                        if game.dictionary.is_valid_word(next_word) and next_word not in visited:
                            if next_word == target:
                                print("\rPath found!                        ")
                                return path + [next_word]
                                
                            # Only add to queue if not at max depth
                            if len(path) < max_depth:
                                visited.add(next_word)
                                queue.append((next_word, path + [next_word]))
        
        if time.time() - start_time >= timeout:
            print("\rTimeout reached - path may exist but is complex        ")
        else:
            print("\rNo path found        ")
        return None
    
    path = check_path_exists(start_word, target_word)
    
    if not path:
        print("\nCouldn't find a transformation path between these words.")
        print("Would you like to create the challenge anyway? (y/n)")
        if input().lower() != 'y':
            return False
    else:
        print(f"\nFound valid path of length {len(path)}!")
        print("Example path:", " → ".join(path))
    
    # Get optional constraints for the word ladder 
    print("\nWould you like to add constraints to make it more challenging? (y/n)")
    if input().lower().startswith('y'):
        # Get banned words
        print("\nEnter banned words (words that cannot be used in the solution)")
        print("Separate multiple words with commas, or press Enter to skip")
        banned = input(": ").strip()
        banned_words = [w.strip() for w in banned.split(',')] if banned else None
        
        # Validate banned words
        if banned_words:
            banned_words = [w for w in banned_words if game.dictionary.is_valid_word(w) and len(w) == len(start_word)]
            if not banned_words:
                print("No valid banned words provided, skipping...")
        
        # Get restricted letters
        print("\nEnter restricted letters (letters that cannot be used)")
        print("Separate multiple letters with commas, or press Enter to skip")
        restricted = input(": ").strip()
        restricted_letters = [l.strip() for l in restricted.split(',')] if restricted else None
        
        # Validate restricted letters
        if restricted_letters:
            restricted_letters = [l for l in restricted_letters if len(l) == 1 and l.isalpha()]
            if not restricted_letters:
                print("No valid restricted letters provided, skipping...")
    else:
        banned_words = None
        restricted_letters = None
    
    # Get max moves for the word ladder 
    min_moves = len(path) - 1 if path else 5  # Default if no path found
    print(f"\nMinimum possible moves: {min_moves}")
    while True:
        try:
            max_moves_input = input(f"Enter maximum allowed moves (minimum {min_moves}, or Enter for default): ").strip()
            if not max_moves_input:
                max_moves = min_moves + 2  # Default: minimum path + 2 extra moves
                break
            max_moves = int(max_moves_input)
            if max_moves >= min_moves:
                break
            print(f"Max moves must be at least {min_moves}!")
        except ValueError:
            print("Please enter a valid number!")
    
    # Create the challenge
    challenge = Challenge(start_word, target_word, max_moves, banned_words, restricted_letters)
    
    # Add challenge to game
    if not game.current_mode:
        game.start_game(DifficultyLevel.BEGINNER, False)
    game.current_mode.challenges.append(challenge)
    
    print("\n✨ Custom challenge created successfully! ✨")
    print(f"Start word: {start_word}")
    print(f"Target word: {target_word}")
    print(f"Maximum moves: {max_moves}")
    if banned_words:
        print(f"Banned words: {', '.join(banned_words)}")
    if restricted_letters:
        print(f"Restricted letters: {', '.join(restricted_letters)}")
    
    # Ask if user wants to play this challenge now
    print("\nWould you like to play this challenge now? (y/n)")
    if input().lower().startswith('y'):
        # Set up the game to play the custom challenge
        game.current_challenge_index = len(game.current_mode.challenges) - 1  # Point to the newly added challenge
        game._start_challenge()  # Start the challenge
        
        clear_screen()
        print_banner()
        print_help()
        
        # Return a flag to indicate we should enter play mode
        return True
    
    return False

def create_word_graph(game: WordLadderGame, depth: int = 2) -> nx.Graph:
    """Create a networkx graph of possible word transformations up to given depth."""
    G = nx.Graph()
    current = game.moves[-1]
    target = game.current_challenge.target_word
    
    # Add initial word
    G.add_node(current)
    
    # BFS to build graph
    words_to_process = {current}
    for _ in range(depth):
        new_words = set()
        for word in words_to_process:
            neighbors = game.dictionary.get_valid_transformations(word)
            for neighbor in neighbors:
                G.add_edge(word, neighbor)
                new_words.add(neighbor)
        words_to_process = new_words
    
    return G

def show_word_graph(game: WordLadderGame) -> None:
    """Display tree-like ASCII visualization of word transformations."""
    if not game.current_challenge:
        return
    
    current = game.moves[-1]
    target = game.current_challenge.target_word
    
    print("\nWord Transformation Tree:")
    print("========================")
    print(f"Current: {current}")
    print(f"Target:  {target} 🎯")
    print("\nPossible Transformations:")
    print("└── " + current)
    
    # Track visited words to avoid cycles
    visited = {current}
    
    def print_transformations(word: str, depth: int = 1, prefix: str = "    "):
        """Recursively print word transformations in tree format."""
        if depth > 2:  # Limit depth for readability
            return
            
        neighbors = game.dictionary.get_valid_transformations(word)
        sorted_neighbors = sorted(neighbors)  # Sort for consistent display
        
        for i, next_word in enumerate(sorted_neighbors):
            if next_word in visited:
                continue
                
            visited.add(next_word)
            
            # Choose the appropriate branch symbol
            is_last = (i == len(sorted_neighbors) - 1)
            branch = "└── " if is_last else "├── "
            
            # Add indicators for special words
            indicator = ""
            if next_word == target:
                indicator = " 🎯 (Target)"
            elif game.current_challenge.banned_words and next_word in game.current_challenge.banned_words:
                indicator = " ❌ (Banned)"
            elif game.current_challenge.restricted_letters and \
                 any(l in next_word for l in game.current_challenge.restricted_letters):
                indicator = " ⚠️ (Restricted)"
            
            # Print the word with its branch
            print(prefix + branch + next_word + indicator)
            
            # Recursively print next level
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_transformations(next_word, depth + 1, next_prefix)
    
    print_transformations(current)

def show_high_scores(game: WordLadderGame) -> None:
    """Display high scores for all difficulty levels."""
    print("\nHigh Scores")
    print("===========")
    for difficulty in DifficultyLevel:
        score = game.high_score_handler.get_high_score(difficulty)
        print(f"{difficulty.name}: {score}")

def get_algorithm_info(algo_name: str) -> str:
    """Get educational information about search algorithms."""
    info = {
        'astar': """
A* Search Algorithm
-----------------
- Combines path cost (g) and heuristic (h) to find optimal path
- g(n): Number of transformations from start
- h(n): Number of differing letters from target
- f(n) = g(n) + h(n): Total estimated cost
- Best for: Finding shortest path efficiently
""",
        'ucs': """
Uniform Cost Search
-----------------
- Explores paths based on actual cost
- No heuristic used
- Guarantees shortest path
- Best for: When all moves have equal cost
""",
        'bfs': """
Breadth First Search
------------------
- Explores all words at current depth before going deeper
- Simple but effective for word ladders
- Guarantees shortest path for unweighted graphs
- Best for: Finding shortest transformation sequence
"""
    }
    return info.get(algo_name, "Algorithm information not available")

# hint function
def load_hint_menu(game: WordLadderGame) -> None:
    """Display educational hint menu with algorithm selection."""
    print("\nAI-Powered Hint System")
    print("=====================")
    
    # Define exception class outside the try block to exit hint menu later and return to main game loop
    class ReturnToMainLoop(Exception):
        pass
    
    # retrives the current and the target words to provide hints
    current_word = game.moves[-1]
    target_word = game.current_challenge.target_word
    print(f"\nCurrent word: {current_word}")
    print(f"Target word: {target_word}")
    
    # check for valid transformations in the dictionary
    valid_transforms = game.dictionary.get_valid_transformations(current_word)
    print(f"Available transformations: {len(valid_transforms)}")
    if not valid_transforms:
        print("\nNo valid transformations possible from current word!")
        input("\nPress Enter to continue...")
        return
    
    # display algo types to the user and ask for their preference 
    print("\nSelect an algorithm to help find the next move:")
    print("1. A* Search      - Optimal pathfinding using heuristics")
    print("2. Uniform Cost   - Systematic exploration of all possibilities")
    print("3. Breadth First  - Layer-by-layer word exploration")
    
    try:
        algo_choice = int(input("\nEnter choice (1-3): "))
        algo_map = {1: 'astar', 2: 'ucs', 3: 'bfs'}
        
        if algo_choice in algo_map:
            algo_name = algo_map[algo_choice]
            
            # Show algorithm information and details on how the algo works
            print(get_algorithm_info(algo_name))
            input("Press Enter to get hint...")
            
            print("Searching for hint...", end="", flush=True)
            
            # Get all possible next words using the selected algorithm
            next_words = valid_transforms
            
            # Remove any words that are banned
            if game.current_challenge.banned_words:
                next_words = [w for w in next_words if w not in game.current_challenge.banned_words]
            
            # Remove words with restricted letters
            if game.current_challenge.restricted_letters:
                next_words = [w for w in next_words if not any(l in w for l in game.current_challenge.restricted_letters)]
            
            # Filter out words already used in the current ladder
            next_words = [w for w in next_words if w not in game.moves]
            
            if not next_words:
                print("\r" + " "*30 + "\r", end="", flush=True)  # Clear progress message
                print("\nNo valid transformations available that meet all constraints!")
                input("\nPress Enter to continue...")
                return
            
            # Simple heuristic: count how many letters match the target word
            def heuristic(word):
                return sum(1 for a, b in zip(word, target_word) if a == b)
            
            # Sort words by heuristic (best first)
            next_words.sort(key=heuristic, reverse=True)
            
            # Pick the first (best) word
            hint = next_words[0]
            
            print("\r" + " "*30 + "\r", end="", flush=True)  # Clear progress message
            
            print(f"\nSuggested next word: {hint}")
            print(f"(Generated using simple heuristic)")
            print("\nWhy this suggestion?")
            print(f"- Changes one letter from '{game.moves[-1]}'")
            print(f"- Has {heuristic(hint)} letters in common with target: '{target_word}'")
            print("- Follows all game constraints")
            print("\n(Using a hint reduces your score by 25 points)")
            
            # Manually update hints counter
            if hasattr(game, 'hints_used'):
                game.hints_used += 1
            
            input("\nPress Enter to continue...")
            
            # Force a clean return to main game loop
            print("\nReturning to game...")
            raise ReturnToMainLoop()
            
        else:
            print("\nInvalid choice!")
            input("\nPress Enter to continue...")
    except ValueError:
        print("\nInvalid input!")
        input("\nPress Enter to continue...")
    except ReturnToMainLoop:
        return  # Ensure we return to main loop

def play_game_loop(game: WordLadderGame) -> None:
    """Main game play loop."""
    while True:  # Challenge loop
        print_game_status(game)
        show_word_graph(game)
        
        # Check if out of moves before taking input
        if game.get_progress_info()['moves_left'] <= 0:
            print("\n❌ Game Over - Out of moves!")
            print(f"Final Score: {game.get_score()}")
            if game.update_high_score():
                print("New High Score! 🏆")
            
            play_again = input("\nWould you like to play again? (y/n): ").lower()
            if play_again != 'y':
                print("\nThanks for playing!")
                return
            break  # Break challenge loop to start new game
        
        command = input("\nEnter command: ").strip().lower().split()
        
        if not command:
            continue
            
        if command[0] == "quit":
            print("\nThanks for playing!")
            return
            
        elif command[0] == "help":
            print_help()
            
        elif command[0] == "show":
            clear_screen()
            print_banner()
            continue
            
        elif command[0] == "hint":
            if game.get_progress_info()['moves_left'] <= 1:
                print("\nNot enough moves left to use a hint!")
                continue
            load_hint_menu(game)
            
        elif command[0] == "move":
            if len(command) != 2:
                print("\nUsage: move <word>")
                continue
                
            if game.make_move(command[1]):
                if game.is_complete():
                    clear_screen()
                    print_game_status(game)
                    print("\n🎉 Congratulations! Challenge completed! 🎉")
                    if game.update_high_score():
                        print("New High Score! 🏆")
                    
                    if game.next_challenge():
                        input("\nPress Enter to start next challenge...")
                        clear_screen()
                    else:
                        print("\n🎮 Game Complete! You've finished all challenges!")
                        play_again = input("\nWould you like to play again? (y/n): ").lower()
                        if play_again != 'y':
                            print("\nThanks for playing!")
                            return
                        break  # Break challenge loop to start new game
            else:
                print("\nInvalid move!")
                if game.get_progress_info()['moves_left'] <= 0:
                    print("❌ Game Over - Out of moves!")
                
        elif command[0] == "restart":
            game._start_challenge()
            clear_screen()
            print("Challenge restarted!")
            
        elif command[0] == "next":
            if game.next_challenge():
                clear_screen()
                print("Moving to next challenge!")
            else:
                print("\nNo more challenges available!")
                
        else:
            print("\nUnknown command. Type 'help' for available commands.")

def save_custom_challenges(game: WordLadderGame) -> None:
    """Save custom challenges to a file for later play."""
    # Create directory if it doesn't exist
    os.makedirs('saved_challenges', exist_ok=True)
    
    try:
        # Load existing challenges if the file exists
        challenges_data = []
        if os.path.exists('saved_challenges/custom_challenges.json'):
            import json
            try:
                with open('saved_challenges/custom_challenges.json', 'r') as f:
                    challenges_data = json.load(f)
            except:
                # If file exists but can't be read, start fresh
                challenges_data = []
        
        # Convert current challenge to serializable format and add to list
        new_challenges = []
        for challenge in game.current_mode.challenges:
            challenge_dict = {
                'start_word': challenge.start_word,
                'target_word': challenge.target_word,
                'max_moves': challenge.max_moves,
                'banned_words': challenge.banned_words or [],
                'restricted_letters': challenge.restricted_letters or []
            }
            new_challenges.append(challenge_dict)
        
        # Add new challenges (avoid duplicates)
        for new_challenge in new_challenges:
            if new_challenge not in challenges_data:
                challenges_data.append(new_challenge)
        
        # Save to file
        import json
        with open('saved_challenges/custom_challenges.json', 'w') as f:
            json.dump(challenges_data, f)
        
        print(f"\nCustom challenges saved successfully! Total: {len(challenges_data)}")
    except Exception as e:
        print(f"\nError saving challenges: {e}")

def load_custom_challenges(game: WordLadderGame) -> bool:
    """Load custom challenges from file and set up game."""
    try:
        # Check if saved challenges exist
        if not os.path.exists('saved_challenges/custom_challenges.json'):
            print("\nNo saved custom challenges found.")
            return False
        
        # Load challenges from file
        import json
        with open('saved_challenges/custom_challenges.json', 'r') as f:
            challenges_data = json.load(f)
        
        if not challenges_data:
            print("\nNo custom challenges found in save file.")
            return False
        
        print(f"\nFound {len(challenges_data)} custom challenges!")
        
        # Create game mode with correct parameter order - difficulty first, then name
        custom_mode = GameMode(DifficultyLevel.BEGINNER, "Custom Challenges")
        
        # Add our custom challenges
        for challenge_dict in challenges_data:
            challenge = Challenge(
                challenge_dict['start_word'],
                challenge_dict['target_word'],
                challenge_dict['max_moves'],
                challenge_dict['banned_words'] or None,
                challenge_dict['restricted_letters'] or None
            )
            custom_mode.challenges.append(challenge)
        
        print(f"Loaded {len(custom_mode.challenges)} custom challenges.")
        
        # Set the mode and current challenge
        game.current_mode = custom_mode
        game.current_challenge_index = 0
        
        # Debug: print first challenge details
        first_challenge = custom_mode.challenges[0]
        print(f"First challenge: {first_challenge.start_word} → {first_challenge.target_word}")
        
        # Now start the challenge
        game._start_challenge()
        
        # Verify the challenge was started correctly
        print(f"Current word: {game.moves[0]}")
        print(f"Target word: {game.current_challenge.target_word}")
        
        return True
    except Exception as e:
        print(f"\nError loading challenges: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    while True:  # Main game loop
        clear_screen()
        print_banner()
        game = WordLadderGame()
        
        print("\nMain Menu:")
        print("1. Play Game")
        print("2. Create Custom Challenge")
        print("3. View High Scores")
        print("4. Quit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            # Difficulty selection
            print("\nSelect Difficulty:")
            print("1. Beginner    - Simple transformations")
            print("2. Advanced    - Longer word chains")
            print("3. Challenge   - Additional constraints")
            
            while True:
                try:
                    choice = int(input("\nEnter choice (1-3): "))
                    if 1 <= choice <= 3:
                        difficulty = list(DifficultyLevel)[choice - 1]
                        break
                except ValueError:
                    pass
                print("Invalid choice. Please enter 1, 2, or 3.")
            
            # Game mode selection
            print("\nSelect Game Mode:")
            print("1. Classic    - Predefined word challenges")
            print("2. Random     - Randomly generated challenges")
            
            while True:
                try:
                    mode_choice = int(input("\nEnter choice (1-2): "))
                    if 1 <= mode_choice <= 2:
                        use_random = (mode_choice == 2)
                        break
                except ValueError:
                    pass
                print("Invalid choice. Please enter 1 or 2.")
            
            # Start game with selected mode
            game.start_game(difficulty, use_random)
            clear_screen()
            print_banner()
            print_help()
            
            # Enter game play loop
            play_game_loop(game)
            
        elif choice == '2':
            play_custom = user_create_custom_challenge(game)
            if play_custom:
                # Start game with the custom challenge
                clear_screen()
                print_banner()
                print_help()
                play_game_loop(game)
                # Save custom challenges after playing
                save_custom_challenges(game)
            else:
                # Save without playing if user chose not to play
                save_custom_challenges(game)
                input("\nPress Enter to continue...")
                
        elif choice == '3':
            show_high_scores(game)
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            print("\nThanks for playing!")
            return
            
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nThanks for playing!")
        sys.exit(0) 