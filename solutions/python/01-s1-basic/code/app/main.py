#!/usr/bin/env python3
"""
Build your own LRU Cache - Stage 1: Basic Cache

Learning objectives:
- Understand cache as key-value store
- Implement get/put operations
- Use Python dict for storage

Stage 1 implements a basic cache without eviction logic.
"""

import sys


class LRUCache:
    """
    Basic cache implementation (Stage 1)
    
    Features:
    - Store key-value pairs
    - Retrieve values by key
    - No eviction (capacity not enforced in Stage 1)
    
    Implementation:
    - Uses Python dict as underlying storage
    - O(1) average time for get and put operations
    """
    
    def __init__(self, capacity: int):
        """
        Initialize cache with given capacity.
        
        Args:
            capacity: Maximum number of items (stored but not enforced in Stage 1)
        
        Note:
            Stage 1 does not implement eviction, so capacity is recorded
            but not actively enforced. This will be implemented in Stage 2.
        """
        self.capacity = capacity
        self.cache = {}  # Simple dictionary for O(1) lookup
    
    def get(self, key: str) -> str | None:
        """
        Retrieve value by key.
        
        Args:
            key: The key to look up
            
        Returns:
            str | None: Value if found, None if key doesn't exist
            
        Time Complexity:
            O(1) average case
            
        Example:
            >>> cache = LRUCache(10)
            >>> cache.put("name", "Alice")
            >>> cache.get("name")
            'Alice'
            >>> cache.get("age")
            None
        """
        return self.cache.get(key)
    
    def put(self, key: str, value: str) -> None:
        """
        Store or update key-value pair.
        
        Args:
            key: The key to store
            value: The value to associate with key
            
        Behavior:
            - If key exists, updates the value
            - If key is new, adds to cache
            - No eviction in Stage 1 (unlimited storage)
            
        Time Complexity:
            O(1) average case
            
        Example:
            >>> cache = LRUCache(10)
            >>> cache.put("name", "Alice")
            >>> cache.put("name", "Bob")  # Updates existing key
            >>> cache.get("name")
            'Bob'
        """
        self.cache[key] = value
    
    def size(self) -> int:
        """
        Return current number of items in cache.
        
        Returns:
            int: Current cache size
            
        Time Complexity:
            O(1)
            
        Example:
            >>> cache = LRUCache(10)
            >>> cache.size()
            0
            >>> cache.put("a", "1")
            >>> cache.size()
            1
        """
        return len(self.cache)


def main():
    """
    Command processor - Main entry point
    
    Reads commands from stdin and writes responses to stdout.
    This is the interface that the tester uses to interact with your cache.
    
    Commands:
        INIT <capacity>     - Initialize cache with given capacity
        PUT <key> <value>   - Store key-value pair
        GET <key>           - Retrieve value (returns NULL if not found)
        SIZE                - Get current cache size
    
    Protocol:
        - All commands are newline-terminated
        - Responses are printed to stdout
        - No logging to stderr (keep it clean for testing)
    
    Example session:
        Input:  INIT 10
        Output: OK
        Input:  PUT name Alice
        Output: OK
        Input:  GET name
        Output: Alice
        Input:  GET age
        Output: NULL
        Input:  SIZE
        Output: 1
    """
    cache = None
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        # Split command, allowing values with spaces
        # maxsplit=2 means: "PUT key value with spaces" -> ["PUT", "key", "value with spaces"]
        parts = line.split(maxsplit=2)
        command = parts[0]
        
        if command == "INIT":
            capacity = int(parts[1])
            cache = LRUCache(capacity)
            print("OK")
        
        elif command == "PUT":
            if cache is None:
                print("ERROR: Cache not initialized")
                continue
            if len(parts) < 3:
                print("ERROR: PUT requires key and value")
                continue
            key = parts[1]
            value = parts[2]
            cache.put(key, value)
            print("OK")
        
        elif command == "GET":
            if cache is None:
                print("ERROR: Cache not initialized")
                continue
            if len(parts) < 2:
                print("ERROR: GET requires key")
                continue
            key = parts[1]
            result = cache.get(key)
            # Return NULL for non-existent keys (not an error)
            print(result if result is not None else "NULL")
        
        elif command == "SIZE":
            if cache is None:
                print("ERROR: Cache not initialized")
                continue
            print(cache.size())
        
        else:
            print(f"ERROR: Unknown command: {command}")


if __name__ == "__main__":
    main()
