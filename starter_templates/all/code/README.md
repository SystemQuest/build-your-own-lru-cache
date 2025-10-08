# Build Your Own LRU Cache

This is a starting point for {{language_name}} solutions to the
**"Build Your Own LRU Cache"** challenge.

An LRU (Least Recently Used) cache is a data structure that stores a limited number of items and removes the least recently used item when the cache is full.

## Quick Start

The entry point for your LRU Cache implementation is in `{{user_editable_file}}`.

### Run locally

```sh
# Run your program
./your_program.sh
```

### Test commands

```sh
INIT 10       # Initialize cache with capacity 10
PUT k1 v1     # Store key-value pair
GET k1        # Retrieve value by key
DELETE k1     # Delete key from cache
EXISTS k1     # Check if key exists
SIZE          # Get current cache size
EXPIRE k1 30  # Set key to expire after 30 seconds
STATS         # Get cache statistics
```

## Challenge Stages

- **Stage 1**: Basic cache operations (GET, PUT, SIZE)
- **Stage 2**: FIFO eviction with capacity limits
- **Stage 3**: LRU eviction using built-in data structures
- **Stage 4**: Custom doubly linked list implementation (Interview Essential)
- **Stage 5**: Thread safety with locks
- **Stage 6**: TTL expiration support
- **Stage 7**: Cache statistics and observability

## Learn More

Visit [SystemQuest](https://systemquest.io) for more challenges.
