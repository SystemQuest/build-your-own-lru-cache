# Stage 3: Implement LRU eviction policy

In this stage, you'll upgrade from FIFO to LRU (Least Recently Used) eviction policy, the industry-standard cache strategy.

## Learning Objectives

By completing this stage, you will:

- Understand the LRU (Least Recently Used) eviction policy
- Learn how access order differs from insertion order
- Implement efficient O(1) get/put operations with LRU tracking
- Discover why LRU is superior for real-world caches

## What is LRU?

**LRU (Least Recently Used)** is the most common cache eviction policy used in production:
- When the cache is full and a new item needs to be inserted
- The **least recently accessed** item is removed to make space
- Both `GET` and `PUT` operations update the access order
- Items that are used frequently stay in the cache longer

### The Key Insight

**Access patterns matter!** If you access a key, it's likely you'll access it again soon. LRU keeps frequently accessed items in cache, improving **hit rate**.

### FIFO vs LRU: The Critical Difference

| Policy | Evicts | Updates order on | Best for |
|--------|--------|------------------|----------|
| **FIFO** | Oldest inserted | (never) | Simple, predictable eviction |
| **LRU** | Least recently used | GET and PUT | Real-world caches (web, database) |

**Example demonstrating the difference:**

```
Cache capacity: 2

FIFO behavior:
PUT a 1  →  Cache: {a:1}
PUT b 2  →  Cache: {a:1, b:2}       (full)
GET a    →  1  (returns value, no order change)
PUT c 3  →  Cache: {b:2, c:3}       (evicts 'a' - oldest inserted)

LRU behavior:
PUT a 1  →  Cache: {a:1}
PUT b 2  →  Cache: {a:1, b:2}       (full)
GET a    →  1  (returns value, 'a' becomes most recent!)
PUT c 3  →  Cache: {a:1, c:3}       (evicts 'b' - least recently used)
```

**Why LRU wins:** In this scenario, we just accessed `a`, so it's likely we'll need it again. LRU keeps it in cache; FIFO throws it away!

## Command Protocol

All commands from Stage 1-2 remain the same. The key differences:

### 1. GET updates access order

In LRU, **reading** a key makes it "recently used":

```
INIT 3
PUT a 1
PUT b 2
PUT c 3      # Cache full: {a:1, b:2, c:3}
GET a        # Access 'a' → now most recent
PUT d 4      # Evicts 'b' (least recently used), not 'a'!
```

**Access order after GET a:** `b` (oldest) → `c` → `a` (newest)

### 2. PUT on existing key updates access order

Unlike FIFO, updating a key in LRU makes it "recently used":

```
INIT 2
PUT a 1
PUT b 2      # Cache: {a:1, b:2}
PUT a 100    # Update 'a' → becomes most recent
PUT c 3      # Evicts 'b' (least recently used), not 'a'
```

**LRU order after PUT a 100:** `b` (oldest) → `a` (newest)

### 3. Eviction always removes least recently used

The item that **hasn't been touched the longest** (by GET or PUT) is evicted first.

## Commands

### INIT \<capacity\>

Initialize the cache with LRU eviction policy.

**Example:**
```
Input:  INIT 5
Output: OK
```

### PUT \<key\> \<value\>

Store or update a key-value pair. **Updates access order** (makes key most recent).

**Example (with eviction):**
```
INIT 2
PUT x 10
PUT y 20     # Cache: {x:10, y:20}
GET x        # Access 'x' → x is most recent
PUT z 30     # Evicts 'y' (least recently used)
GET y        # Returns NULL (evicted)
GET z        # Returns '30'
```

**Example (update existing key):**
```
INIT 2
PUT a 1
PUT b 2      # Cache: {a:1, b:2}
PUT a 3      # Update 'a' → 'a' becomes most recent
PUT c 4      # Evicts 'b', not 'a'
GET a        # Returns '3' (still in cache)
GET b        # Returns NULL (evicted)
```

### GET \<key\>

Retrieve value for a key. **Updates access order** if key exists.

**Example:**
```
INIT 2
PUT a 1
PUT b 2
GET a        # Returns '1' AND makes 'a' most recent
PUT c 3      # Now evicts 'b' (not 'a')
```

**Returns:** `<value>` or `NULL`

### SIZE

Returns the current number of items in the cache.

**Example:**
```
Input:  SIZE
Output: 3
```

## Implementation Guide

### The Classic LRU Data Structure

LRU caches typically use a combination of two data structures:
- **HashMap/Dictionary**: Provides O(1) key lookup
- **Ordered Data Structure**: Maintains access order for O(1) eviction

### Implementation Strategy

The challenge: track which items are "recently used" and which are "least recently used" efficiently.

**Core Questions to Solve:**
1. How do you efficiently track access order?
2. How do you quickly find the least recently used item to evict?
3. How do you update the access order when a key is accessed or updated?

**Think about:**
- What data structure maintains both O(1) lookup AND order?
- How can you move an item to represent "recently used"?
- Where should "most recent" and "least recent" items live?

### Language-Specific Hints

| Language | Recommended Data Structure | Why? |
|----------|---------------------------|------|
| **Python** | `OrderedDict` from `collections` | Has a `.move_to_end()` method |
| **Java** | `LinkedHashMap` | Constructor parameter enables access-order |
| **Go** | `container/list` + `map` | Manual implementation needed |

**Your task:** Research these data structures in your language's documentation and discover how they help solve the LRU problem.

### Complexity Target

Your implementation should achieve:
- `get(key)`: O(1) time
- `put(key, value)`: O(1) time
- `size()`: O(1) time
- Space: O(capacity)

**Challenge:** Can you achieve O(1) for all operations? 💡

## Test Cases

Your implementation will be tested with:

### 1. Basic LRU eviction (GET updates order)

```
INIT 2
PUT a 1
PUT b 2
GET a        # Access 'a' → becomes most recent
PUT c 3      # Should evict 'b' (least recently used)
GET a        # Returns '1' (kept in cache)
GET b        # Returns NULL (evicted)
GET c        # Returns '3'
```

**Expected behavior:** After `GET a`, the order is `b` (oldest) → `a` (newest), so adding `c` evicts `b`.

### 2. LRU vs FIFO (PUT updates order)

```
INIT 2
PUT a 1
PUT b 2
PUT a 100    # Update 'a' → becomes most recent in LRU
PUT c 3      # Should evict 'b' (least recently used)
GET a        # Returns '100' (kept)
GET b        # Returns NULL (evicted)
GET c        # Returns '3'
```

**This is the key difference from FIFO!** In FIFO, `a` would be evicted (oldest insertion). In LRU, `b` is evicted (least recently used).

### 3. Multiple accesses

```
INIT 3
PUT a 1
PUT b 2
PUT c 3      # Cache full: {a:1, b:2, c:3}
GET a        # Access 'a'
GET b        # Access 'b'
PUT d 4      # Should evict 'c' (only unaccessed key)
GET c        # Returns NULL (evicted)
GET a        # Returns '1'
GET b        # Returns '2'
GET d        # Returns '4'
SIZE         # Returns 3
```

**Expected behavior:** `c` is the only key that wasn't accessed, so it's evicted first.

### 4. Sequential evictions with access pattern

```
INIT 2
PUT a 1
PUT b 2      # Cache: {a:1, b:2}
PUT c 3      # Evicts 'a' (LRU)
PUT d 4      # Evicts 'b' (LRU)
GET c        # Access 'c' → becomes most recent
PUT e 5      # Should evict 'd' (not 'c')
GET c        # Returns '3' (kept)
GET d        # Returns NULL (evicted)
GET e        # Returns '5'
```

**Expected behavior:** Accessing `c` protects it from eviction.

## Common Pitfalls to Avoid

### ❌ Pitfall 1: Not updating access order on GET

Remember: In LRU, **reading** a key makes it recently used!

**Wrong approach:**
- Just return the value without updating position

**Correct approach:**
- Mark the key as "most recently used" before returning the value

---

### ❌ Pitfall 2: Not updating order when updating existing key

Remember: In LRU (unlike FIFO), **updating** a key makes it recently used!

**Wrong approach:**
- Only update the value, don't change the access order

**Correct approach:**
- Update both the value AND mark as "most recently used"

---

### ❌ Pitfall 3: Evicting when updating an existing key

**Wrong approach:**
- Check capacity and evict before checking if key exists
- This wastes an eviction on a simple update

**Correct approach:**
- First check if key already exists
- Only evict if you're adding a NEW key and at capacity

---

### ❌ Pitfall 4: Using inefficient data structures

**Wrong approach:**
- Using only a regular dictionary/map (loses order information)
- Using only a list (O(n) lookups)

**Correct approach:**
- Use a data structure that maintains both O(1) lookup AND order
- Or combine two data structures to achieve both properties

## Testing Your Implementation

Run the tester against your implementation:

```bash
cd /path/to/your/solution
export SYSTEMQUEST_REPOSITORY_DIR=.
export SYSTEMQUEST_TEST_CASES_JSON='[{"slug":"ch7","tester_log_prefix":"stage-3.1","title":"LRU Eviction"}]'
/path/to/lru-cache-tester/dist/tester
```

Or use the Makefile:

```bash
make test_stage3
```

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| `get(key)` | O(1) | O(1) |
| `put(key, value)` | O(1) | O(1) |
| `size()` | O(1) | O(1) |
| Overall | O(1) | O(capacity) |

**Why O(1)?**
- HashMap: O(1) lookup
- OrderedDict/Linked List: O(1) move-to-front, O(1) delete-from-head

## Real-World Applications

LRU is the industry-standard eviction policy used in:
- **Web Browsers** - Recently visited pages stay in memory
- **Databases** - MySQL, PostgreSQL query result caching
- **In-Memory Stores** - Redis, Memcached (default policy)
- **Operating Systems** - Page cache for file I/O

**Why LRU?** It balances simplicity with effectiveness, achieving high hit rates in most scenarios.

## Summary

**You've accomplished:**
- ✅ Implemented LRU eviction (least recently used)
- ✅ Understood how GET and PUT update access order
- ✅ Leveraged language built-in data structures
- ✅ Grasped why LRU > FIFO for real-world caches
- ✅ Achieved O(1) performance for all operations

**Key takeaways:**
- Access order is critical in LRU (unlike FIFO's insertion order)
- Both GET and PUT operations update the "recently used" status
- Efficient implementation requires maintaining both lookup speed and order
- LRU is the industry standard for most caching scenarios

## What's Next?

Congratulations! 🎉 You've built a working LRU cache that mirrors production systems like Redis and Memcached.

**More stages coming soon:** Custom data structures, thread safety, and production features.

**Keep building!** 🚀

## Additional Resources

- [LRU Cache (LeetCode #146)](https://leetcode.com/problems/lru-cache/) - Classic interview problem
- [Redis Eviction Policies](https://redis.io/docs/reference/eviction/) - How Redis implements LRU
- [Cache Replacement Policies](https://en.wikipedia.org/wiki/Cache_replacement_policies) - Deep dive
