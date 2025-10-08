import sys


class LRUCache:
    def __init__(self, capacity: int):
        """Initialize LRU Cache with given capacity"""
        # Uncomment this to pass the first stage
        # self.capacity = capacity
        # self.cache = {}
    
    def get(self, key: str) -> str | None:
        """Get value by key, return None if not found"""
        # Uncomment this to pass the first stage
        # return self.cache.get(key)
    
    def put(self, key: str, value: str) -> None:
        """Insert or update key-value pair"""
        # Uncomment this to pass the first stage
        # self.cache[key] = value
    
    def size(self) -> int:
        """Return the number of items in the cache"""
        # Uncomment this to pass the first stage
        # return len(self.cache)


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)
    
    cache = None
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        command = parts[0]
        
        if command == "INIT":
            capacity = int(parts[1])
            cache = LRUCache(capacity)
            print("OK")
        
        elif command == "PUT":
            if cache is None:
                print("ERROR: Cache not initialized")
                continue
            key = parts[1]
            value = parts[2]
            cache.put(key, value)
            print("OK")
        
        elif command == "GET":
            if cache is None:
                print("ERROR: Cache not initialized")
                continue
            key = parts[1]
            result = cache.get(key)
            if result is None:
                print("NULL")
            else:
                print(result)
        
        elif command == "SIZE":
            if cache is None:
                print("ERROR: Cache not initialized")
                continue
            print(cache.size())
        
        else:
            print(f"ERROR: Unknown command: {command}")


if __name__ == "__main__":
    main()
