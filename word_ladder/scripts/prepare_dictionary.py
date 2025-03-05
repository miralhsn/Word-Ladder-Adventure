from pathlib import Path
#creating a sample dictionary 
def create_simple_dictionary():
    """Create a dictionary with common English words."""
    # Common English words that work well for word ladder
    word_list = """
    cat dog rat bat hat mat pat sat fat
    big bag bug beg bog dig dog dug hug
    word ward warm worm work walk talk
    play clay slay stay stag star
    stone store score scare spare space spade
    peace place plane plate
    money honey
    """.split()
    
    # Create resources directory if it doesn't exist
    resources_dir = Path(__file__).parent.parent / 'resources'
    resources_dir.mkdir(exist_ok=True)
    
    # Clean and sort words
    cleaned_words = sorted(set(word.strip().lower() for word in word_list if word.strip()))
    
    # Save to file
    dictionary_path = resources_dir / 'dictionary.txt'
    with open(dictionary_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_words))
    
    print(f"Dictionary created with {len(cleaned_words)} words")
    print(f"Saved to: {dictionary_path}")

if __name__ == "__main__":
    create_simple_dictionary() 