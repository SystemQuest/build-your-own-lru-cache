# Stage 2: Implement FIFO eviction policy

In this stage, you'll add capacity enforcement and implement a FIFO (First-In-First-Out) eviction policy.

## Learning Objectives

By completing this stage, you will:

- Understand cache eviction policies and why they're necessary
- Implement FIFO (First-In-First-Out) eviction strategy
- Learn to track insertion order while maintaining O(1) operations
- Handle capacity limits correctly

## What is FIFO?

**FIFO (First-In-First-Out)** is the simplest cache eviction policy:
- When the cache is full and a new item needs to be inserted
- The **oldest** item (first inserted) is removed to make space
- It's like a queue: first in, first out

### FIFO vs LRU

| Policy | Evicts | Tracks |
|--------|--------|--------|
| **FIFO** | Oldest inserted item | Insertion order |
| **LRU** (Stage 3) | Least recently used item | Access order |

**Example:**
```
Cache capacity: 2

PUT a 1  →  Cache: {a:1}
PUT b 2  →  Cache: {a:1, b:2}  (full)
PUT c 3  →  Cache: {b:2, c:3}  (evicted 'a', oldest)
GET b    →  2  (access doesn't affect FIFO order)
PUT d 4  →  Cache: {c:3, d:4}  (evicted 'b', oldest)
```

## Command Protocol

All commands from Stage 1 remain the same. The key difference:

### Capacity Enforcement

When `PUT` is called and the cache is at full capacity:
1. Remove the **oldest** item (first inserted)
2. Insert the new item

### Important Behaviors

#### 1. PUT on existing key does NOT change order

```
INIT 2
PUT a 1  →  Cache: {a:1}
PUT b 2  →  Cache: {a:1, b:2}
PUT a 3  →  Cache: {a:3, b:2}  ⚠️ 'a' updated, order unchanged
PUT c 4  →  Cache: {b:2, c:4}  (evicted 'a', still oldest)
```

**Key point:** Updating an existing key should **not** move it to the end of the insertion order.

#### 2. SIZE returns current count

```
INIT 3
SIZE     →  0
PUT a 1  →  OK
SIZE     →  1
PUT b 2  →  OK
PUT c 3  →  OK
SIZE     →  3
PUT d 4  →  OK  (evicts 'a')
SIZE     →  3  (still at capacity)
```

## Commands

### INIT \<capacity\>

Initialize the cache with a given capacity (same as Stage 1, but now enforced).

**Example:**
```
Input:  INIT 5
Output: OK
```

### PUT \<key\> \<value\>

Store a key-value pair. If at capacity, evict the oldest item first.

**Example (at capacity):**
```
INIT 2
PUT x 10
PUT y 20
PUT z 30   # Evicts 'x' (oldest), inserts 'z'
GET x      # Returns NULL (evicted)
GET z      # Returns '30'
```

### GET \<key\>

Retrieve value for a key. Returns `NULL` if not found.

**Example:**
```
Input:  GET mykey
Output: myvalue
```

or

```
Input:  GET notfound
Output: NULL
```

### SIZE

Returns the current number of items in the cache.

**Example:**
```
Input:  SIZE
Output: 3
```

## Implementation Tips

### Option 1: Python List (Simple)

Use a list to track insertion order:

```python
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}        # key -> value
        self.order = []        # track insertion order
    
    def put(self, key, value):
        if key not in self.cache and len(self.cache) >= self.capacity:
            # Evict oldest (first in list)
            oldest = self.order.pop(0)
            del self.cache[oldest]
        
        if key not in self.cache:
            self.order.append(key)  # Only add if new key
        
        self.cache[key] = value
```

**Complexity:** O(n) for eviction due to `list.pop(0)`

### Option 2: Python OrderedDict (Better)

Use `collections.OrderedDict` which maintains insertion order:

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def put(self, key, value):
        if key not in self.cache and len(self.cache) >= self.capacity:
            # Evict oldest (FIFO)
            self.cache.popitem(last=False)  # Remove first item
        
        if key in self.cache:
            # Update without changing order (for FIFO)
            self.cache[key] = value
        else:
            # Add new key
            self.cache[key] = value
```

**Complexity:** O(1) average case

## Test Cases

Your implementation will be tested with:

1. **Basic FIFO eviction**
   ```
   INIT 2
   PUT 1 one
   PUT 2 two
   PUT 3 three  # Should evict '1'
   GET 1        # Should return NULL
   GET 2        # Should return 'two'
   GET 3        # Should return 'three'
   ```

2. **Update existing key (order unchanged)**
   ```
   INIT 2
   PUT a 1
   PUT b 2
   PUT a 3      # Update 'a', doesn't move to end
   PUT c 4      # Should evict 'a' (still oldest)
   GET a        # Should return NULL
   ```

3. **SIZE with eviction**
   ```
   INIT 3
   PUT x 1
   PUT y 2
   PUT z 3
   SIZE         # Returns 3
   PUT w 4      # Evicts oldest
   SIZE         # Still returns 3
   ```

## Common Mistakes

❌ **Moving updated keys to end of order**
```python
# WRONG for FIFO
if key in self.cache:
    self.order.remove(key)
    self.order.append(key)  # Don't do this!
```

✅ **Correct: Only track order for new keys**
```python
# CORRECT for FIFO
if key not in self.cache:
    self.order.append(key)  # Only add if new
```

---

❌ **Forgetting to check capacity before adding**
```python
# WRONG
def put(self, key, value):
    if len(self.cache) >= self.capacity:
        # This will evict even when updating existing key!
        self.cache.popitem(last=False)
```

✅ **Correct: Only evict if adding NEW key**
```python
# CORRECT
def put(self, key, value):
    if key not in self.cache and len(self.cache) >= self.capacity:
        self.cache.popitem(last=False)
```

## Testing Your Implementation

Run the tester against your implementation:

```bash
cd /path/to/your/solution
SYSTEMQUEST_REPOSITORY_DIR=. /path/to/lru-cache-tester/dist/tester
```

Or use the test script:

```bash
make test_stage2
```

## What's Next?

In **Stage 3**, you'll upgrade from FIFO to **LRU (Least Recently Used)** eviction:
- Track **access order** (not just insertion order)
- Evict the **least recently accessed** item
- Update order on both `GET` and `PUT` operations

FIFO is simple but not optimal. LRU is the industry-standard cache eviction policy! 🚀

## Additional Resources

- [Cache Replacement Policies (Wikipedia)](https://en.wikipedia.org/wiki/Cache_replacement_policies)
- [Python OrderedDict Documentation](https://docs.python.org/3/library/collections.html#collections.OrderedDict)
- FIFO vs LRU: Understanding the difference

## Summary

- ✅ Implement capacity enforcement
- ✅ Evict oldest item when full (FIFO)
- ✅ Maintain insertion order
- ✅ Don't reorder on key updates
- ✅ SIZE returns current count

Good luck! 💪
