In this stage, you'll upgrade from FIFO to LRU (Least Recently Used) eviction - the industry-standard cache policy.

This is where your cache becomes **production-ready**, matching the behavior of Redis, Memcached, and browser caches.

### LRU vs FIFO

<details>
<summary>Background: Why LRU is better</summary>

**FIFO (Stage 2)**: Evicts based on insertion order
- Simple, predictable
- Ignores access patterns
- Bad hit rate for real workloads

**LRU (this stage)**: Evicts based on access order
- Keeps frequently used items
- Both `GET` and `PUT` update "recently used" status
- Much better hit rate in practice

**Key difference:**
```
Cache capacity: 2

FIFO:
PUT a 1  →  {a:1}
PUT b 2  →  {a:1, b:2}
GET a    →  1 (no order change)
PUT c 3  →  {b:2, c:3}  ← evicts 'a' (oldest insertion)

LRU:
PUT a 1  →  {a:1}
PUT b 2  →  {a:1, b:2}
GET a    →  1 (a becomes most recent!)
PUT c 3  →  {a:1, c:3}  ← evicts 'b' (least recently used)
```

**Why LRU wins:** We just accessed `a`, so we'll likely need it again. LRU keeps it; FIFO throws it away.

</details>

---

### Implementation Requirements

To pass this stage, your program will need to:

1. **Track access order, not just insertion order**
   - Both `GET` and `PUT` operations must update the access timestamp
   
2. **Evict the least recently used item when full**
   - Not the oldest inserted item (that's FIFO)
   
3. **Use an ordered data structure** that supports:
   - O(1) lookup by key
   - O(1) reordering (move to end)
   - O(1) eviction from front

**Recommended data structures:**
- Python: `OrderedDict` (has `.move_to_end()` method)
- Java: `LinkedHashMap` (with `accessOrder=true` constructor parameter)
- Go: `container/list` + `map` (manual implementation)

**All operations must remain O(1).**

---

### Tests

The tester will execute your program like this:

```bash
$ ./your_program.sh
```

It will then send commands to verify LRU behavior. **The tester runs 4 test scenarios** to ensure your implementation correctly handles access order, not insertion order.

#### Test 1: Basic LRU eviction (GET updates order)

```bash
$ echo -e "INIT 2\nPUT a 1\nPUT b 2\nGET a\nPUT c 3\nGET a\nGET b\nGET c" | ./your_program.sh
OK
OK
OK
1       # GET a makes 'a' most recent
OK      # PUT c evicts 'b' (least recently used)
1       # a still in cache
NULL    # b was evicted
3       # c in cache
```

**Expected behavior:**
- After `GET a`, the access order is: `b` (least recent) → `a` (most recent)
- Adding `c` evicts `b`, not `a`
- If you evict `a` instead, you implemented FIFO, not LRU

#### Test 2: LRU vs FIFO (PUT updates order)

```bash
$ echo -e "INIT 2\nPUT a 1\nPUT b 2\nPUT a 100\nPUT c 3\nGET a\nGET b\nGET c" | ./your_program.sh
OK
OK
OK
OK      # PUT a 100 makes 'a' most recent
OK      # PUT c evicts 'b' (not 'a'!)
100     # a retained
NULL    # b evicted
3       # c in cache
```

**This is the key difference from FIFO!**
- In FIFO: `a` would be evicted (oldest insertion)
- In LRU: `b` is evicted (least recently used, because `PUT a 100` updated access time)

#### Test 3: Multiple access patterns

```bash
$ echo -e "INIT 3\nPUT a 1\nPUT b 2\nPUT c 3\nGET a\nGET b\nPUT d 4\nGET a\nGET b\nGET c\nGET d\nSIZE" | ./your_program.sh
OK
OK
OK
OK
1       # Access a
2       # Access b
OK      # d evicts c (only unaccessed item)
1       # a in cache
2       # b in cache
NULL    # c evicted
4       # d in cache
3       # SIZE is 3
```

**Expected behavior:**
- `c` is the only item not accessed after insertion
- When adding `d`, evict `c` (least recently used)

#### Test 4: Sequential evictions

```bash
$ echo -e "INIT 2\nPUT a 1\nPUT b 2\nPUT c 3\nPUT d 4\nGET c\nPUT e 5\nGET c\nGET d\nGET e" | ./your_program.sh
OK
OK
OK
OK      # c evicts a
OK      # d evicts b
3       # Access c
OK      # e evicts d (not c, because c was just accessed)
3       # c in cache
NULL    # d evicted
5       # e in cache
```

**Expected behavior:**
- Access order is maintained through multiple evictions
- `GET c` protects `c` from being evicted next

---

### Notes

<details>
<summary>OrderedDict in Python</summary>

Python's `OrderedDict` (from `collections`) is perfect for LRU:

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key):
        if key not in self.cache:
            return None
        # Move to end (mark as recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            # Update existing key - move to end
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Evict LRU if over capacity
        if len(self.cache) > self.capacity:
            # popitem(last=False) removes the first (least recent) item
            self.cache.popitem(last=False)
```

**Key methods:**
- `.move_to_end(key)` - Move key to end (most recent)
- `.popitem(last=False)` - Remove first item (least recent)

</details>

<details>
<summary>LinkedHashMap in Java</summary>

Java's `LinkedHashMap` can maintain access order:

```java
import java.util.LinkedHashMap;
import java.util.Map;

class LRUCache extends LinkedHashMap<String, String> {
    private int capacity;
    
    public LRUCache(int capacity) {
        // accessOrder=true: maintain access order (not insertion order)
        super(capacity, 0.75f, true);
        this.capacity = capacity;
    }
    
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, String> eldest) {
        // Automatically evict when size > capacity
        return size() > capacity;
    }
    
    public String get(String key) {
        return super.getOrDefault(key, null);
    }
}
```

**Key parameter:**
- `accessOrder=true` - Automatically reorders on `get()` and `put()`
- `removeEldestEntry()` - Hook called after each insertion

</details>

<details>
<summary>Common pitfalls</summary>

**1. Not updating order on GET**
```python
# ❌ WRONG - just returns value
def get(self, key):
    return self.cache.get(key)

# ✅ CORRECT - updates access order
def get(self, key):
    if key not in self.cache:
        return None
    self.cache.move_to_end(key)  # Mark as recently used!
    return self.cache[key]
```

**2. Not updating order when updating existing key**
```python
# ❌ WRONG - doesn't update order
def put(self, key, value):
    self.cache[key] = value
    if len(self.cache) > self.capacity:
        self.cache.popitem(last=False)

# ✅ CORRECT - updates order before setting value
def put(self, key, value):
    if key in self.cache:
        self.cache.move_to_end(key)  # Update access time!
    self.cache[key] = value
    if len(self.cache) > self.capacity:
        self.cache.popitem(last=False)
```

**3. Evicting when updating existing key**
```python
# ❌ WRONG - evicts even when just updating
def put(self, key, value):
    if len(self.cache) >= self.capacity:  # Wrong check!
        self.cache.popitem(last=False)
    self.cache[key] = value

# ✅ CORRECT - only evict when adding NEW key
def put(self, key, value):
    if key in self.cache:
        self.cache.move_to_end(key)
    self.cache[key] = value
    if len(self.cache) > self.capacity:  # Check AFTER insertion
        self.cache.popitem(last=False)
```

</details>

<details>
<summary>Why not use a regular dict?</summary>

Regular dictionaries/maps don't maintain order (or maintain insertion order, not access order):

```python
# ❌ Regular dict - no access order tracking
cache = {}  # Python 3.7+ maintains insertion order, but not access order!

# When you do cache['a'], there's no way to "move it to the end"
# You'd need to delete and re-insert, which is O(n) in some languages
```

**Ordered data structures solve this:**
- They maintain a doubly linked list internally
- Moving an item to the end is O(1) pointer updates
- Evicting from the front is O(1) pointer updates

In Stage 4, you'll implement this doubly linked list manually!

</details>

---

### Resources

- [LRU Cache (LeetCode 146)](https://leetcode.com/problems/lru-cache/) - You'll implement this manually in Stage 4
- [Python OrderedDict](https://docs.python.org/3/library/collections.html#collections.OrderedDict) - Official documentation
- [Redis LRU Eviction](https://redis.io/docs/reference/eviction/) - How Redis implements LRU in production
- [Cache Replacement Policies](https://en.wikipedia.org/wiki/Cache_replacement_policies) - Theory behind LRU, LFU, etc.
