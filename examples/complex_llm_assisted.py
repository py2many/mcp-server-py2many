"""
Example Python code that benefits from LLM-assisted translation.

These examples use complex Python idioms, decorators, dynamic behavior,
and patterns that may not translate well with deterministic rules alone.
"""

from functools import wraps


# Example 1: Decorator with state
def memoize(func):
    """Decorator that caches function results."""
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper


@memoize
def fibonacci(n):
    """Calculate nth Fibonacci number with memoization."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# Example 2: Complex comprehensions
def process_user_data(users):
    """
    Process user data with complex filtering and transformation.
    This uses nested comprehensions with multiple conditions.
    """
    return {
        user['id']: {
            'name': user['name'].upper(),
            'email': user['email'].lower(),
            'scores': [s * 10 for s in user.get('scores', []) if s >= 0.5],
            'average': sum(user.get('scores', [])) / len(user.get('scores', [1]))
        }
        for user in users
        if user.get('active') 
        and user.get('age', 0) >= 18
        and len(user.get('scores', [])) >= 3
    }


# Example 3: Context manager
class DatabaseConnection:
    """Context manager for database connections."""
    
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
    
    def __enter__(self):
        # Simulate connection
        self.connection = f"Connection({self.connection_string})"
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Simulate cleanup
        self.connection = None
        return False


# Example 4: Dynamic attribute access
class DynamicConfig:
    """Configuration class with dynamic attribute access."""
    
    def __init__(self):
        self._data = {}
    
    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(f"No attribute {name}")
        return self._data.get(name)
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value


# Example 5: Generator with complex logic
def batch_process(items, batch_size=10):
    """
    Process items in batches with filtering and transformation.
    Uses generator with complex control flow.
    """
    batch = []
    for item in items:
        if item is None or item == '':
            continue
        
        processed = item.strip().lower() if isinstance(item, str) else str(item)
        batch.append(processed)
        
        if len(batch) >= batch_size:
            yield batch
            batch = []
    
    if batch:
        yield batch


if __name__ == "__main__":
    # Test memoized fibonacci
    print(f"Fibonacci(10): {fibonacci(10)}")
    
    # Test user data processing
    users = [
        {'id': 1, 'name': 'Alice', 'email': 'ALICE@EXAMPLE.COM', 
         'active': True, 'age': 25, 'scores': [0.8, 0.9, 0.7]},
        {'id': 2, 'name': 'Bob', 'email': 'bob@test.com',
         'active': True, 'age': 17, 'scores': [0.9, 0.8, 0.9]},
    ]
    print(f"Processed users: {process_user_data(users)}")
    
    # Test context manager
    with DatabaseConnection("postgresql://localhost/db") as conn:
        print(f"Connected: {conn}")
    
    # Test dynamic config
    config = DynamicConfig()
    config.database_url = "postgres://localhost"
    config.debug_mode = True
    print(f"Config database_url: {config.database_url}")
    
    # Test batch processing
    items = ["  Hello  ", "", "WORLD", None, "  test  "]
    for i, batch in enumerate(batch_process(items, 2)):
        print(f"Batch {i}: {batch}")
