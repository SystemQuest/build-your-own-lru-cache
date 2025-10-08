In this stage, you'll add capacity enforcement and implement FIFO (First-In-First-Out) eviction.

FIFO is the simplest eviction policy - like a queue, the oldest item gets evicted first.

### FIFO Eviction

<details>
<summary>Background: What is FIFO?</summary>

**FIFO (First-In-First-Out)** evicts the oldest inserted item when the cache is full.

```
Cache capacity: 2

PUT a 1  →  {a:1}
PUT b 2  →  {a:1, b:2}         (full)
PUT c 3  →  {b:2, c:3}         (evicts 'a', oldest)
GET b    →  2
PUT d 4  →  {c:3, d:4}         (evicts 'b', oldest)
```

**Key property:** Eviction order is based on **insertion time**, not access time.

**FIFO vs LRU preview:**

| Policy | Evicts | Tracks | Use case |
|--------|--------|--------|----------|
| **FIFO** (this stage) | Oldest inserted | Insertion order | Simple caches, predictable eviction |
| **LRU** (Stage 3) | Least recently used | Access order | Production caches (Redis, browsers) |

**Important:** In FIFO, updating an existing key does NOT change its position in the eviction queue.

```
PUT a 1  →  {a:1}
PUT b 2  →  {a:1, b:2}
PUT a 100 → {a:100, b:2}       ('a' updated but still oldest)
PUT c 3  →  {b:2, c:3}         (evicts 'a', not 'b')
```

</details>

---

### Implementation Requirements

To pass this stage, your program will need to:

1. **Track insertion order** of keys
   - Need to know which item was inserted first
   
2. **Evict the oldest item when at capacity**
   - Only evict when adding a NEW key (not when updating)
   - Check `if key not in cache and len(cache) >= capacity`
   
3. **Don't reorder on updates**
   - Updating an existing key should NOT change its position
   - Key difference from LRU (coming in Stage 3)

**Recommended approach:**
- Python: Use `dict` + `list` to track insertion order
- Or use `OrderedDict` (maintains insertion order)

**All operations should remain O(1) amortized.**

---

### Tests

The tester will execute your program like this:

```bash
$ ./your_program.sh
```

It will then send commands to verify FIFO behavior. **The tester runs 3 test scenarios** to ensure your implementation correctly evicts based on insertion order (not access order).

#### Test 1: Basic FIFO eviction

```bash
$ echo -e "INIT 2\nPUT a 1\nPUT b 2\nPUT c 3\nGET a\nGET b\nGET c" | ./your_program.sh
OK
OK
OK
OK      # PUT c evicts 'a' (oldest)
NULL    # a was evicted
2       # b still in cache
3       # c in cache
```

**Expected behavior:**
- Cache capacity is 2
- When `PUT c 3` is called, cache is full
- Evict `a` (first inserted), not `b`

#### Test 2: Update doesn't change eviction order

```bash
$ echo -e "INIT 2\nPUT a 1\nPUT b 2\nPUT a 100\nPUT c 3\nGET a\nGET b\nGET c" | ./your_program.sh
OK
OK
OK
OK      # PUT a 100 updates value, doesn't change order
OK      # PUT c evicts 'a' (still oldest!)
NULL    # a was evicted (not b!)
2       # b still in cache
3       # c in cache
```

**This is the key FIFO property!**
- `PUT a 100` updates the value but doesn't move `a` to the end
- `a` is still the oldest inserted item
- When adding `c`, evict `a` (not `b`)

**Note:** This will be different in LRU (Stage 3), where `PUT a 100` would make `a` "recently used" and protect it from eviction.

#### Test 3: SIZE with eviction

```bash
$ echo -e "INIT 3\nPUT a 1\nSIZE\nPUT b 2\nPUT c 3\nSIZE\nPUT d 4\nSIZE\nGET a" | ./your_program.sh
OK
OK
1       # SIZE after adding 1 item
OK
OK
3       # SIZE at capacity
OK      # d evicts a
3       # SIZE still at capacity (not 4!)
NULL    # a was evicted
```

**Expected behavior:**
- SIZE increases as items are added
- SIZE doesn't exceed capacity
- SIZE remains at capacity after evictions

---

### Notes

<details>
<summary>Implementation approach: dict + list</summary>

Python 3.7+ dictionaries maintain insertion order, but you still need to track which key to evict:

```python
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.insertion_order = []  # Track insertion order
    
    def get(self, key):
        return self.cache.get(key)
    
    def put(self, key, value):
        # If key exists, update value but DON'T change order
        if key in self.cache:
            self.cache[key] = value
            return
        
        # If at capacity, evict oldest
        if len(self.cache) >= self.capacity:
            oldest_key = self.insertion_order.pop(0)  # Remove first
            del self.cache[oldest_key]
        
        # Add new item
        self.cache[key] = value
        self.insertion_order.append(key)
    
    def size(self):
        return len(self.cache)
```

**Complexity:**
- `get()`: O(1)
- `put()`: O(n) worst case due to `list.pop(0)`, O(1) amortized
- `size()`: O(1)

**Note:** `list.pop(0)` is O(n), but for small caches this is acceptable. In Stage 4, you'll learn how to achieve true O(1) with a doubly linked list.

</details>

<details>
<summary>Alternative: OrderedDict (Python)</summary>

Python's `OrderedDict` can also work for FIFO:

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key):
        return self.cache.get(key)
    
    def put(self, key, value):
        # If key exists, update without reordering
        if key in self.cache:
            self.cache[key] = value
            return
        
        # If at capacity, evict oldest
        if len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)  # Remove first item
        
        # Add new item
        self.cache[key] = value
    
    def size(self):
        return len(self.cache)
```

**Key method:**
- `.popitem(last=False)` - Removes the first (oldest) item in O(1)

**Caveat:** Don't use `.move_to_end()` in this stage - that's for LRU (Stage 3)!

</details>

<details>
<summary>Common pitfalls</summary>

**1. Reordering on update (wrong for FIFO)**
```python
# ❌ WRONG - this is LRU behavior, not FIFO!
def put(self, key, value):
    if key in self.cache:
        # Don't remove and re-add for FIFO!
        self.insertion_order.remove(key)
        self.insertion_order.append(key)
    # ...

# ✅ CORRECT - FIFO doesn't reorder on update
def put(self, key, value):
    if key in self.cache:
        self.cache[key] = value  # Just update value
        return  # Don't change order!
    # ...
```

**2. Evicting when updating existing key**
```python
# ❌ WRONG - evicts even when just updating
def put(self, key, value):
    if len(self.cache) >= self.capacity:
        # This will evict even if key already exists!
        oldest = self.insertion_order.pop(0)
        del self.cache[oldest]
    self.cache[key] = value

# ✅ CORRECT - only evict when adding NEW key
def put(self, key, value):
    if key in self.cache:
        self.cache[key] = value
        return
    
    # Only evict if adding NEW key at capacity
    if len(self.cache) >= self.capacity:
        oldest = self.insertion_order.pop(0)
        del self.cache[oldest]
    
    self.cache[key] = value
    self.insertion_order.append(key)
```

**3. Not removing from insertion_order list**
```python
# ❌ WRONG - memory leak, list grows forever
def put(self, key, value):
    if len(self.cache) >= self.capacity:
        oldest = self.insertion_order.pop(0)
        # Forgot to delete from cache!
    self.cache[key] = value
    self.insertion_order.append(key)

# ✅ CORRECT - remove from BOTH structures
def put(self, key, value):
    if key in self.cache:
        self.cache[key] = value
        return
    
    if len(self.cache) >= self.capacity:
        oldest = self.insertion_order.pop(0)
        del self.cache[oldest]  # Also delete from cache!
    
    self.cache[key] = value
    self.insertion_order.append(key)
```

</details>

<details>
<summary>FIFO vs LRU comparison</summary>

Understanding FIFO helps you appreciate LRU (Stage 3):

**FIFO example:**
```
INIT 2
PUT a 1  →  {a:1}
PUT b 2  →  {a:1, b:2}
GET a    →  1 (no order change in FIFO!)
PUT c 3  →  {b:2, c:3} (evicts 'a')
```

**LRU example (Stage 3 preview):**
```
INIT 2
PUT a 1  →  {a:1}
PUT b 2  →  {a:1, b:2}
GET a    →  1 (moves 'a' to end - "recently used")
PUT c 3  →  {a:1, c:3} (evicts 'b', not 'a'!)
```

**Key difference:** LRU tracks **access order**, FIFO tracks **insertion order**.

In real-world caches, LRU is almost always better because frequently accessed items stay in cache longer.

</details>

---

### Resources

- [Cache Replacement Policies (Wikipedia)](https://en.wikipedia.org/wiki/Cache_replacement_policies) - Overview of FIFO, LRU, LFU, etc.
- [Python OrderedDict](https://docs.python.org/3/library/collections.html#collections.OrderedDict) - Official documentation
- [Amortized Analysis](https://en.wikipedia.org/wiki/Amortized_analysis) - Why `list.pop(0)` is O(1) amortized for small caches
