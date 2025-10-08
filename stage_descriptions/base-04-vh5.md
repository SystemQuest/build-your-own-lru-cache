# Stage 4: Implement custom doubly linked list

In this stage, you'll rebuild the LRU cache **from scratch** using a HashMap and a manually implemented doubly linked list. This is the classic LeetCode interview problem!

## Learning Objectives

By completing this stage, you will:

- Understand how high-level abstractions like `OrderedDict` work under the hood
- Implement a doubly linked list with pointer manipulation
- Combine HashMap + Doubly Linked List for O(1) LRU operations
- Master the classic "LeetCode 146: LRU Cache" problem
- Grasp why dummy/sentinel nodes simplify boundary conditions

## Why Reimplement LRU?

**Stage 3** used `OrderedDict` (Python) or similar built-in data structures:
- ✅ **Pros:** Fast to implement, production-ready
- ❌ **Cons:** Black box, doesn't teach underlying mechanics

**Stage 4** implements the data structure manually:
- ✅ **Pros:** Deep understanding, interview essential, transferable to any language
- ❌ **Cons:** More code, pointer bugs, edge cases

### The Interview Perspective

**LeetCode 146 (LRU Cache)** is one of the most popular interview questions at companies like:
- Google, Amazon, Microsoft, Meta
- Uber, Lyft, Netflix
- Bloomberg, Goldman Sachs

**Interviewers want to see:**
1. Can you design a data structure that achieves O(1) for all operations?
2. Do you understand how to manipulate pointers in a doubly linked list?
3. Can you handle edge cases (empty cache, capacity=1, etc.)?

**This stage prepares you to ace that interview!** 🎯

## Stage 3 vs Stage 4: What Changes?

### Same Behavior, Different Implementation

| Aspect | Stage 3 | Stage 4 |
|--------|---------|---------|
| **Functionality** | LRU eviction | LRU eviction (identical) |
| **Commands** | INIT, PUT, GET, SIZE | INIT, PUT, GET, SIZE (same) |
| **Complexity** | O(1) for all ops | O(1) for all ops (same) |
| **Data Structure** | `OrderedDict` | HashMap + Manual DLL |
| **Code Lines** | ~30 lines | ~120 lines |
| **Interview Relevance** | Low | ⭐ High ⭐ |

**Key insight:** All test cases from Stage 3 will still pass in Stage 4. You're just replacing the "magic" `OrderedDict` with your own implementation.

## The Classic Data Structure Design

### High-Level Architecture

```
LRU Cache = HashMap (for O(1) lookup) + Doubly Linked List (for O(1) reordering)

HashMap: key -> Node
         {
           "a": Node(key="a", value="1"),
           "b": Node(key="b", value="2"),
           ...
         }

Doubly Linked List: (maintains access order)
         head <-> Node(a) <-> Node(b) <-> Node(c) <-> tail
         (dummy)  ↑ most recent      least recent ↑  (dummy)
```

### Why This Combination?

| Data Structure | Provides | Time Complexity |
|----------------|----------|-----------------|
| **HashMap** | Fast key lookup | O(1) get |
| **Doubly Linked List** | Fast reordering & eviction | O(1) move/delete |

**Without HashMap:** Finding a node would require O(n) traversal of the list.
**Without DLL:** Moving an item to "most recent" would require O(n) reordering.

### The Node Structure

Each node in the doubly linked list needs:

```python
class Node:
    def __init__(self, key, value):
        self.key = key      # ⚠️ Key is needed for HashMap cleanup!
        self.value = value
        self.prev = None    # Pointer to previous node
        self.next = None    # Pointer to next node
```

**Critical question:** Why does Node store the `key` when HashMap already maps key->Node?

<details>
<summary>💡 Click to reveal answer</summary>

When evicting the LRU node (at `tail.prev`), you need to delete it from the HashMap too. Without storing the key in the node, you wouldn't know which HashMap entry to delete!

```python
def _remove_lru(self):
    lru_node = self.tail.prev
    self._remove_node(lru_node)
    del self.cache[lru_node.key]  # ← Need key here!
```
</details>

### Dummy Nodes (Sentinels)

**The problem with boundary conditions:**

```python
# Without dummy nodes - lots of special cases! ❌
def _add_to_head(self, node):
    if self.head is None:        # Empty list
        self.head = self.tail = node
    elif self.head == self.tail:  # Single element
        self.head.next = node
        node.prev = self.head
        self.tail = node
    else:                         # Multiple elements
        node.next = self.head
        self.head.prev = node
        self.head = node
```

**With dummy nodes - no special cases! ✅**

```python
# Dummy nodes simplify everything!
def __init__(self, capacity):
    self.head = Node("", "")  # Dummy head
    self.tail = Node("", "")  # Dummy tail
    self.head.next = self.tail
    self.tail.prev = self.head

def _add_to_head(self, node):
    # Always have head and tail, no None checks needed
    node.next = self.head.next
    node.prev = self.head
    self.head.next.prev = node
    self.head.next = node
```

**Dummy nodes** are sentinel values that:
- Eliminate `None` checks
- Simplify pointer operations
- Reduce bug surface area
- Are a common pattern in linked list implementations

**List structure with dummy nodes:**
```
head (dummy) <-> Node(a) <-> Node(b) <-> tail (dummy)
     ↑ never None            never None ↑
```

## Implementation Roadmap

### Phase 1: Define the Node Class

Create a node that stores key, value, and pointers:

```python
class Node:
    def __init__(self, key: str, value: str):
        # TODO: Implement
        pass
```

**Questions to answer:**
- What fields does Node need? (key, value, prev, next)
- Should Node be a separate class or nested inside LRUCache?
- How will you initialize prev/next? (None initially, updated when inserted)

### Phase 2: Initialize LRUCache with Dummy Nodes

```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # HashMap: key -> Node
        
        # TODO: Create dummy head and tail
        # TODO: Connect head.next = tail, tail.prev = head
```

**After initialization, your list should look like:**
```
head <-> tail
(no real nodes yet, just dummies)
```

### Phase 3: Implement Helper Methods

These are the building blocks for your LRU operations:

#### 3.1: `_remove_node(node)`

Remove a node from the doubly linked list:

```
Before: prev <-> node <-> next
After:  prev <-------> next
```

**Think about:**
- Which pointers need to be updated? (prev.next, next.prev)
- What order should you update them in?
- Do you need to handle None cases? (No! Dummy nodes prevent this)

**Pseudo-code skeleton:**
```python
def _remove_node(self, node: Node) -> None:
    # Step 1: Save references to neighbors
    # Step 2: Update prev's next pointer
    # Step 3: Update next's prev pointer
```

#### 3.2: `_add_to_head(node)`

Insert a node right after the dummy head (most recent position):

```
Before: head <-> first <-> ...
After:  head <-> node <-> first <-> ...
```

**Think about:**
- Which pointers need to be updated? (4 pointers: node.next, node.prev, head.next, first.prev)
- What if the list is empty (head.next == tail)? (Same logic! Dummy nodes ftw)

**Pseudo-code skeleton:**
```python
def _add_to_head(self, node: Node) -> None:
    # Step 1: Get the current first node (head.next)
    # Step 2: Set node's pointers
    # Step 3: Update first node's prev pointer
    # Step 4: Update head's next pointer
```

#### 3.3: `_move_to_head(node)`

Mark a node as "most recently used" by moving it to the head:

```python
def _move_to_head(self, node: Node) -> None:
    # Hint: Can you reuse _remove_node and _add_to_head?
    pass
```

**This should be a simple two-liner!** 💡

#### 3.4: `_remove_lru()`

Evict the least recently used node (the one before tail):

```python
def _remove_lru(self) -> None:
    # TODO: Find the LRU node (tail.prev)
    # TODO: Remove it from the DLL
    # TODO: Remove it from the HashMap (don't forget this!)
```

**Common mistake:** Forgetting to delete from the HashMap! The node will disappear from the DLL but still occupy memory.

### Phase 4: Implement Public Methods

#### `get(key)`

```python
def get(self, key: str) -> str | None:
    # 1. Check if key exists in HashMap
    # 2. If not, return None
    # 3. If yes, move node to head (mark as recently used)
    # 4. Return node's value
```

**Time complexity target:** O(1)
- HashMap lookup: O(1)
- Move to head: O(1) (pointer operations)

#### `put(key, value)`

```python
def put(self, key: str, value: str) -> None:
    if key in self.cache:
        # Case 1: Key exists - update value and move to head
        pass
    else:
        # Case 2: New key - add node, check capacity
        # If at capacity, evict LRU first
        pass
```

**Think carefully about the order of operations:**
1. Should you check capacity before or after checking if key exists?
2. When do you call `_remove_lru()`?
3. Do you always call `_add_to_head()` for new keys?

**Time complexity target:** O(1)
- HashMap insert: O(1)
- Add to head: O(1)
- Remove LRU: O(1)

#### `size()`

```python
def size(self) -> int:
    return len(self.cache)  # Easy! HashMap knows its size
```

## Pointer Manipulation: The Critical Details

### Correct Order Matters!

**Wrong order can lose references:**

```python
# ❌ WRONG: Loses reference to original head.next
def _add_to_head(self, node):
    self.head.next = node  # Lost reference to old first node!
    node.next = ???        # Can't access old first anymore
```

**Correct order saves references first:**

```python
# ✅ CORRECT: Save reference before modifying
def _add_to_head(self, node):
    first = self.head.next       # Save reference
    node.next = first            # Use saved reference
    node.prev = self.head
    first.prev = node
    self.head.next = node
```

### Visualizing Pointer Updates

**Adding a node:**
```
Step 0: head <-> A <-> tail
        
Step 1: Create node B
        head <-> A <-> tail
        B (disconnected)

Step 2: Set B's pointers
        head <-> A <-> tail
        ↓      ↗
        B ─────

Step 3: Update A's prev
        head    A <-> tail
        ↓      ↗↓
        B ─────

Step 4: Update head's next
        head    A <-> tail
         ↓↘    ↗↓
         B ────

Final:  head <-> B <-> A <-> tail
```

**Pro tip:** Draw diagrams on paper when debugging pointer operations!

## Common Pitfalls

### ❌ Pitfall 1: Not storing key in Node

**Problem:**
```python
class Node:
    def __init__(self, value):
        self.value = value
        # No key! ❌
```

**Why it fails:**
When evicting, you need to delete from HashMap but don't know which key to delete.

**Solution:** Always store key in Node.

---

### ❌ Pitfall 2: Forgetting to update HashMap on eviction

**Problem:**
```python
def _remove_lru(self):
    lru_node = self.tail.prev
    self._remove_node(lru_node)
    # Forgot: del self.cache[lru_node.key] ❌
```

**Why it fails:**
- Node removed from DLL but still in HashMap
- Memory leak (old entries never freed)
- SIZE will be incorrect

**Solution:** Always update both data structures together.

---

### ❌ Pitfall 3: Updating pointers in wrong order

**Problem:**
```python
def _remove_node(self, node):
    node.prev.next = node.next  # OK so far
    node.next.prev = node.prev  # Still OK
    node.next = None            # Unnecessary
    node.prev = None            # Unnecessary
```

**This actually works, but the last two lines are optional.** The node will be garbage collected when no longer referenced.

**However, this fails:**
```python
def _add_to_head(self, node):
    self.head.next = node       # Lost reference! ❌
    node.next = self.head.next  # Now points to node itself! Bug!
```

**Solution:** Save references before modifying pointers.

---

### ❌ Pitfall 4: Not handling capacity correctly on PUT

**Problem:**
```python
def put(self, key, value):
    if len(self.cache) >= self.capacity:
        self._remove_lru()  # ❌ Evicts even when updating existing key!
    # ... rest of logic
```

**Why it fails:**
If the key already exists, you're just updating it, not adding a new entry. You shouldn't evict in this case!

**Solution:** Only evict if adding a NEW key AND at capacity.

```python
if key not in self.cache and len(self.cache) >= self.capacity:
    self._remove_lru()  # ✅ Only evict for new keys
```

## Testing Your Implementation

### Phase 1: Unit Test Individual Methods

Test each helper method separately:

```python
# Test _add_to_head
cache = LRUCache(3)
node = Node("a", "1")
cache._add_to_head(node)
assert cache.head.next == node
assert node.prev == cache.head

# Test _remove_node
cache._remove_node(node)
assert cache.head.next == cache.tail
```

### Phase 2: Test Against Stage 3 Cases

Your Stage 4 implementation should pass **all Stage 3 test cases**:

```bash
# Run Stage 3 tests against Stage 4 implementation
cd /path/to/lru-cache-tester
SYSTEMQUEST_REPOSITORY_DIR=/path/to/stage4/code \
SYSTEMQUEST_TEST_CASES_JSON='[...]' \
./dist/tester
```

**If Stage 3 tests fail, your LRU logic is wrong!**

### Phase 3: Test Stage 4 Specific Cases

Stage 4 adds tests for edge cases:

1. **Capacity = 1** (minimal cache)
   ```
   INIT 1
   PUT a 1
   PUT b 2  # Should evict 'a' immediately
   GET a    # NULL
   GET b    # '2'
   ```

2. **Empty cache operations**
   ```
   INIT 5
   SIZE     # 0
   GET x    # NULL (empty cache)
   PUT a 1
   SIZE     # 1
   ```

3. **Repeated operations on same key**
   ```
   INIT 2
   PUT a 1
   GET a    # Access multiple times
   GET a
   PUT a 2  # Update multiple times
   PUT a 3
   # Verify 'a' doesn't create duplicate nodes in DLL
   ```

4. **Full eviction cycle**
   ```
   INIT 2
   PUT a 1
   PUT b 2  # Full
   PUT c 3  # Evict 'a'
   PUT d 4  # Evict 'b'
   # Cache now empty of original keys, only {c:3, d:4}
   ```

## Complexity Analysis

| Operation | Time | Space | Why? |
|-----------|------|-------|------|
| `get(key)` | O(1) | O(1) | HashMap lookup + pointer ops |
| `put(key, value)` | O(1) | O(1) | HashMap insert + pointer ops |
| `size()` | O(1) | O(1) | HashMap size property |
| Overall | O(1) | O(capacity) | Fixed number of nodes |

**Proof of O(1):**
- HashMap operations: O(1) average case
- DLL operations: O(1) worst case (fixed number of pointer updates)
- No loops over cache contents (would be O(n))

**This is the optimal solution!** There's no faster way to implement LRU.

## Real-World Context

### Where is this used?

1. **Redis** - Uses a similar approach (with approximate LRU for memory efficiency)
2. **Memcached** - Classic LRU with doubly linked list
3. **Linux Kernel** - Page cache uses LRU lists
4. **Database Buffers** - MySQL, PostgreSQL buffer pools
5. **CDNs** - Akamai, Cloudflare edge caches

### Interview Companies

Companies that frequently ask this question:
- **FAANG:** Google, Amazon, Meta, Apple, Netflix
- **Unicorns:** Uber, Lyft, Airbnb, DoorDash
- **Finance:** Goldman Sachs, Bloomberg, Jane Street
- **Enterprise:** Microsoft, Oracle, Salesforce

**Preparation tip:** After completing this stage, solve [LeetCode 146](https://leetcode.com/problems/lru-cache/) to verify your understanding!

## Summary

**You've accomplished:**
- ✅ Implemented Node class with key, value, prev, next
- ✅ Used dummy nodes to simplify boundary conditions
- ✅ Built a doubly linked list from scratch
- ✅ Combined HashMap + DLL for O(1) LRU operations
- ✅ Mastered pointer manipulation and edge cases
- ✅ Prepared for LeetCode 146 interview question

**Key insights:**
- High-level abstractions (OrderedDict) hide complex implementations
- Dummy nodes eliminate special cases and simplify code
- Storing key in Node is essential for HashMap cleanup
- Pointer order matters - save references before modifying
- O(1) LRU requires both HashMap (lookup) and DLL (reordering)

## What's Next?

**Stage 5 (Coming Soon)** will add production features:
- Thread safety (locks, concurrent access)
- TTL (Time To Live) for automatic expiration
- Metrics (hit rate, eviction count, latency)
- Memory management (size limits, value serialization)

**From interview to production!** 🚀

## Additional Resources

### Essential
- [LeetCode 146 - LRU Cache](https://leetcode.com/problems/lru-cache/) - **Practice this!**
- [Doubly Linked List - Wikipedia](https://en.wikipedia.org/wiki/Doubly_linked_list)
- [Sentinel Nodes](https://en.wikipedia.org/wiki/Sentinel_node)

### Advanced
- [LRU-K Algorithm](https://en.wikipedia.org/wiki/Page_replacement_algorithm#Least_recently_used) - LRU with look-ahead
- [ARC (Adaptive Replacement Cache)](https://en.wikipedia.org/wiki/Adaptive_replacement_cache) - Better than LRU
- [Redis LRU Implementation](https://redis.io/docs/reference/eviction/) - Production approach

### Videos
- [LeetCode 146 Solution Walkthrough](https://www.youtube.com/results?search_query=leetcode+146+lru+cache)
- [Doubly Linked List Visualization](https://visualgo.net/en/list)

---

**Ready to tackle the interview?** Go build your custom DLL and ace that coding challenge! 💪
