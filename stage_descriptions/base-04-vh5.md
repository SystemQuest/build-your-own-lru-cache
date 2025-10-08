In this stage, you'll rebuild the LRU cache using a HashMap and a manually implemented doubly linked list.

This is the classic [LeetCode 146](https://leetcode.com/problems/lru-cache/) interview problem, frequently asked at Google, Amazon, and Meta.

### HashMap + Doubly Linked List

<details>
<summary>Background: Why this combination?</summary>

In Stage 3, you used a built-in ordered dictionary (`OrderedDict`, `LinkedHashMap`, etc.). While convenient, it's a "black box" that doesn't teach the underlying mechanics.

In this stage, you'll implement the data structure manually:

```
LRU Cache = HashMap + Doubly Linked List

HashMap: O(1) lookup by key
DLL:     O(1) reordering and eviction
```

**Why both?**
- HashMap alone can't track access order efficiently
- DLL alone can't find nodes in O(1) time

**Visual structure:**
```
HashMap:
┌─────┬────────┐
│ "a" │ Node─┐ │
│ "b" │ Node─┼─┼───┐
│ "c" │ Node─┼─┼───┼───┐
└─────┴────────┘ │   │   │
                 ↓   ↓   ↓
Doubly Linked List (access order):
head ←→ [a:1] ←→ [b:2] ←→ [c:3] ←→ tail
(dummy) ↑ most recent    least ↑  (dummy)
```

The HashMap maps keys to nodes in the DLL. When you `GET` or `PUT`, you move the node to the head (most recent). When evicting, you remove the node before tail (least recent).

</details>

---

### Implementation Requirements

To pass this stage, your program will need to:

1. **Define a Node class** with fields: `key`, `value`, `prev`, `next`
2. **Use dummy head/tail nodes** to eliminate edge cases
3. **Implement 4 helper methods:**
   - `_remove_node(node)` - Remove node from DLL
   - `_add_to_head(node)` - Insert node after head
   - `_move_to_head(node)` - Mark node as recently used
   - `_remove_lru()` - Evict least recently used node
4. **Update `get()` to call `_move_to_head()`** (mark as recently used)
5. **Update `put()` to handle capacity** (evict when adding new key at capacity)

**All operations must remain O(1).**

---

### Tests

The tester will execute your program like this:

```bash
$ ./your_program.sh
```

It will then send a series of commands to test LRU behavior. **The tester runs 8 different test scenarios**, covering edge cases like empty cache, capacity=1, sequential evictions, and full eviction cycles. Here are the 3 most important ones:

#### Test 1: Basic LRU eviction

```bash
$ echo -e "INIT 2\nPUT a 1\nPUT b 2\nGET a\nPUT c 3\nGET a\nGET b\nGET c" | ./your_program.sh
OK
OK
OK
1       # GET a returns 1 (a is now most recent)
OK      # PUT c evicts b (not a, because a was just accessed)
1       # a is still in cache
NULL    # b was evicted
3       # c is in cache
```

**Expected behavior:**
- After `GET a`, node `a` moves to the head (most recent)
- When `PUT c` with cache full, evict node before tail (which is `b`)
- If you evict `a` instead, you implemented FIFO, not LRU

#### Test 2: Capacity = 1

```bash
$ echo -e "INIT 1\nPUT a 1\nPUT b 2\nGET a\nGET b" | ./your_program.sh
OK
OK
OK      # PUT b immediately evicts a
NULL    # a was evicted
2       # b is in cache
```

#### Test 3: Repeated operations on same key

```bash
$ echo -e "INIT 2\nPUT a 1\nPUT a 2\nPUT a 3\nSIZE\nPUT b 4\nPUT c 5\nGET a\nGET b\nGET c" | ./your_program.sh
OK
OK
OK
OK
1       # SIZE is 1 (not 3!)
OK      # b added
OK      # c added, should evict a (not b!)
NULL    # a was evicted
4       # b is still in cache
3       # c is in cache
```

**Expected behavior:**
- Repeated PUT on same key should NOT create duplicate nodes
- SIZE should not increase when updating existing keys
- When capacity is reached, evict the LEAST recently used key
- In this case: after `PUT c 5`, 'a' is evicted (not 'b'), because 'b' was added AFTER the last `PUT a 3`

---

### Notes

<details>
<summary>About the 8 test scenarios</summary>

Manual pointer management is error-prone, so the tester checks multiple edge cases:

1. **Basic LRU eviction** - Core LRU behavior (shown above)
2. **LRU vs FIFO** - PUT on existing key updates access order
3. **Multiple access patterns** - Repeated GET operations
4. **Sequential evictions** - Multiple evictions in a row
5. **Capacity = 1** - Smallest possible cache (stresses boundary conditions)
6. **Empty cache** - Operations on uninitialized cache
7. **Repeated operations** - No duplicate nodes, correct SIZE (shown above)
8. **Full eviction cycle** - Fill → evict all → refill (DLL recovery test)

Each edge case corresponds to common bugs in real interviews. The 3 tests shown above cover the most critical patterns.

</details>

<details>
<summary>Dummy nodes pattern</summary>

**Dummy (sentinel) nodes** simplify boundary conditions:

```python
# Without dummy nodes - many edge cases
if self.head is None:        # Empty list
    # special logic
elif self.head == self.tail:  # Single element
    # different logic
else:                         # Normal case
    # normal logic

# With dummy nodes - one unified logic
def _add_to_head(self, node):
    # head and tail are never None!
    node.next = self.head.next
    node.prev = self.head
    self.head.next.prev = node
    self.head.next = node
```

Initial state after initialization:
```
head ←→ tail
(empty list, only dummies)
```

</details>

<details>
<summary>Why store key in Node?</summary>

When evicting the LRU node, you need to delete it from the HashMap:

```python
def _remove_lru(self):
    lru_node = self.tail.prev
    self._remove_node(lru_node)
    del self.cache[lru_node.key]  # ← Need key here!
```

Without storing the key in the node, you wouldn't know which HashMap entry to delete.

</details>

<details>
<summary>Common pitfalls</summary>

**1. Wrong pointer update order**
```python
# ❌ WRONG - loses reference
def _add_to_head(self, node):
    self.head.next = node          # Lost old first!
    node.next = self.head.next     # Now points to node itself!

# ✅ CORRECT - save first
def _add_to_head(self, node):
    first = self.head.next         # Save reference
    node.next = first              # Use saved reference
    node.prev = self.head
    first.prev = node
    self.head.next = node
```

**2. Forgot to update HashMap on eviction**
```python
# ❌ WRONG - memory leak
def _remove_lru(self):
    lru_node = self.tail.prev
    self._remove_node(lru_node)    # Only removes from list

# ✅ CORRECT
def _remove_lru(self):
    lru_node = self.tail.prev
    self._remove_node(lru_node)
    del self.cache[lru_node.key]   # Also remove from HashMap!
```

**3. Evicting when updating existing key**
```python
# ❌ WRONG
def put(self, key, value):
    if len(self.cache) >= self.capacity:
        self._remove_lru()          # Evicts even when updating!
    # ...

# ✅ CORRECT
def put(self, key, value):
    if key in self.cache:
        # Update existing - no eviction
        node = self.cache[key]
        node.value = value
        self._move_to_head(node)
    else:
        # New key - may need eviction
        if len(self.cache) >= self.capacity:
            self._remove_lru()
        # ...
```

</details>

<details>
<summary>Implementation skeleton</summary>

Here's a skeleton to get you started:

```python
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        
        # Create dummy nodes
        self.head = Node("", "")
        self.tail = Node("", "")
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
        # TODO: Remove node from DLL
        pass
    
    def _add_to_head(self, node):
        # TODO: Insert node after head
        pass
    
    def _move_to_head(self, node):
        # TODO: Remove and add to head
        pass
    
    def _remove_lru(self):
        # TODO: Evict node before tail
        pass
    
    def get(self, key):
        # TODO: Return value and move to head
        pass
    
    def put(self, key, value):
        # TODO: Add/update and handle capacity
        pass
    
    def size(self):
        return len(self.cache)
```

</details>

---

### Resources

- [LeetCode 146 - LRU Cache](https://leetcode.com/problems/lru-cache/) - Practice this problem after completing the stage
- [Doubly Linked List Visualization](https://visualgo.net/en/list) - Visual tool for understanding pointer operations
- [Sentinel Nodes](https://en.wikipedia.org/wiki/Sentinel_node) - Learn more about the dummy node pattern
