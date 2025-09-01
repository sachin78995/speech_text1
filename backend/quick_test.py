import re

def remove_repeated_words(text):
    if not text or not text.strip():
        return text
    
    words = text.split()
    cleaned = []
    
    for i, word in enumerate(words):
        # Remove punctuation for comparison but keep original word
        current_word_clean = re.sub(r'[^\w]', '', word.lower())
        
        if i == 0:
            cleaned.append(word)
        else:
            previous_word_clean = re.sub(r'[^\w]', '', words[i-1].lower())
            # Keep the word if it's different from the previous word (ignoring punctuation)
            if current_word_clean != previous_word_clean:
                cleaned.append(word)
    
    return ' '.join(cleaned)

# Test with your example
test_text = 'Hello, hello. I am Pagan from K&D.'
result = remove_repeated_words(test_text)
print(f'Original: "{test_text}"')
print(f'Cleaned:  "{result}"')

# Test with more examples
test_cases = [
    "hello hello world",
    "Hello, hello. I am here",
    "this this is is a test",
    "word word, word.",
]

print("\nMore test cases:")
for test in test_cases:
    cleaned = remove_repeated_words(test)
    print(f'"{test}" -> "{cleaned}"')
