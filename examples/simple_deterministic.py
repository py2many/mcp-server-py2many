"""
Example Python code suitable for deterministic translation.

These examples use simple, well-structured Python patterns that
translate well using py2many's deterministic rules.
"""

# Example 1: Simple mathematical function
def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


# Example 2: List operations
def sum_even_numbers(numbers):
    """Sum all even numbers in a list."""
    return sum(n for n in numbers if n % 2 == 0)


# Example 3: Basic algorithm
def find_max(numbers):
    """Find the maximum value in a list."""
    if not numbers:
        return None
    max_val = numbers[0]
    for n in numbers[1:]:
        if n > max_val:
            max_val = n
    return max_val


# Example 4: String manipulation
def reverse_words(text):
    """Reverse the order of words in a string."""
    words = text.split()
    return " ".join(reversed(words))


# Example 5: Simple class
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)


if __name__ == "__main__":
    # Test the functions
    print(f"Factorial of 5: {factorial(5)}")
    print(f"Sum of evens [1,2,3,4,5,6]: {sum_even_numbers([1, 2, 3, 4, 5, 6])}")
    print(f"Max of [3,1,4,1,5,9]: {find_max([3, 1, 4, 1, 5, 9])}")
    print(f"Reverse words: {reverse_words('Hello World')}")
    
    rect = Rectangle(5, 3)
    print(f"Rectangle area: {rect.area()}")
    print(f"Rectangle perimeter: {rect.perimeter()}")
