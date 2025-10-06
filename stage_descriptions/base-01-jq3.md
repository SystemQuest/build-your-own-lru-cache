# Stage 1: Implement basic cache

In this stage, you'll implement a basic key-value cache that can store and retrieve items.

## Learning Objectives

By completing this stage, you will:

- Understand the fundamental concept of a cache as a key-value store
- Learn to implement `get(key)` and `put(key, value)` operations
- Use Python's built-in dictionary for O(1) average-case lookup
- Handle stdin/stdout communication for command processing

## Command Protocol

Your program should read commands from **stdin** and write responses to **stdout**.

### Commands

#### 1. INIT \<capacity\>

Initialize the cache with a given capacity.

**Arguments:**
- `capacity`: Maximum number of items the cache can hold (integer)

**Response:** `OK`

**Example:**
```
Input:  INIT 10
Output: OK
```

**Notes:**
- In Stage 1, capacity is stored but not enforced (no eviction yet)
- Eviction logic will be added in Stage 2

---

#### 2. PUT \<key\> \<value\>

Store a key-value pair in the cache. If the key already exists, update its value.

**Arguments:**
- `key`: The key to store (string, no spaces)
- `value`: The value to associate with the key (string, may contain spaces)

**Response:** `OK`

**Example:**
```
Input:  PUT name Alice
Output: OK

Input:  PUT message hello world
Output: OK
```

**Notes:**
- Keys cannot contain spaces
- Values may contain spaces (everything after the key is treated as the value)
- If key exists, the old value is replaced

---

#### 3. GET \<key\>

Retrieve the value associated with a key.

**Arguments:**
- `key`: The key to look up (string)

**Response:** 
- `<value>` if key exists
- `NULL` if key doesn't exist

**Example:**
```
Input:  GET name
Output: Alice

Input:  GET age
Output: NULL
```

**Notes:**
- Return exactly `NULL` (not "null", "None", or empty string) for non-existent keys
- In Stage 1, GET does not affect eviction order

---

#### 4. SIZE

Return the current number of items in the cache.

**Arguments:** None

**Response:** `<number>` (current cache size as integer)

**Example:**
```
Input:  SIZE
Output: 3
```

---

## Example Session

Here's a complete interaction demonstrating all commands:

```
Input:  INIT 10
Output: OK

Input:  PUT name Alice
Output: OK

Input:  PUT age 30
Output: OK

Input:  GET name
Output: Alice

Input:  GET city
Output: NULL

Input:  SIZE
Output: 2

Input:  PUT name Bob
Output: OK

Input:  GET name
Output: Bob

Input:  SIZE
Output: 2
```

**Key observations:**
- After `PUT name Bob`, the size remains 2 (key was updated, not added)
- `GET city` returns `NULL` because the key doesn't exist
- All commands are processed sequentially

---

## Implementation Guide

### Data Structure

Use a Python dictionary to store key-value pairs:

```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # Simple dict for O(1) lookup
```

**Why dict?**
- O(1) average-case get/put operations
- Built-in, no external dependencies
- Perfect for Stage 1 (no eviction needed yet)

---

### Method Signatures

```python
def get(self, key: str) -> str | None:
    """Retrieve value by key, return None if not found"""
    return self.cache.get(key)

def put(self, key: str, value: str) -> None:
    """Store or update key-value pair"""
    self.cache[key] = value

def size(self) -> int:
    """Return current cache size"""
    return len(self.cache)
```

---

### Command Processing

Read commands line by line from stdin:

```python
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    # Split with maxsplit=2 to allow spaces in values
    parts = line.split(maxsplit=2)
    command = parts[0]
    
    if command == "INIT":
        capacity = int(parts[1])
        cache = LRUCache(capacity)
        print("OK")
    
    elif command == "PUT":
        key = parts[1]
        value = parts[2]
        cache.put(key, value)
        print("OK")
    
    elif command == "GET":
        key = parts[1]
        result = cache.get(key)
        print(result if result is not None else "NULL")
    
    elif command == "SIZE":
        print(cache.size())
```

**Important:** Use `maxsplit=2` when splitting to preserve spaces in values!

---

## Common Pitfalls

### 1. ❌ Returning wrong value for missing keys

```python
# WRONG: Returns empty string
def get(self, key):
    return self.cache.get(key, "")

# CORRECT: Returns None, print handles NULL
def get(self, key):
    return self.cache.get(key)
```

**Remember:** Print `NULL` for non-existent keys, not empty string or "None".

---

### 2. ❌ Not handling key updates correctly

```python
# WRONG: Always appends, doesn't update
if key not in self.cache:
    self.cache[key] = value  # Only adds new keys

# CORRECT: Dict automatically updates
self.cache[key] = value  # Updates if exists, adds if new
```

**Remember:** Python dict automatically handles both insert and update.

---

### 3. ❌ Splitting commands incorrectly

```python
# WRONG: Loses spaces in values
parts = line.split()  # "PUT msg hello world" -> ["PUT", "msg", "hello", "world"]

# CORRECT: Preserves spaces in values
parts = line.split(maxsplit=2)  # -> ["PUT", "msg", "hello world"]
```

**Remember:** Use `maxsplit=2` for PUT command to preserve value spaces.

---

### 4. ❌ Not initializing cache before use

```python
# WRONG: Using cache before INIT
cache = LRUCache(10)  # At module level

# CORRECT: Initialize on INIT command
cache = None
if command == "INIT":
    cache = LRUCache(capacity)
```

**Remember:** Wait for INIT command before creating cache instance.

---

### 5. ❌ Forgetting to implement SIZE

```python
# WRONG: SIZE not implemented
elif command == "SIZE":
    print("0")  # Always returns 0

# CORRECT: Return actual cache size
elif command == "SIZE":
    print(cache.size())
```

**Remember:** SIZE should return the actual number of items in the cache.

---

## Testing Your Implementation

### Manual Testing

You can test your implementation manually:

```bash
cd code
printf "INIT 10\nPUT name Alice\nGET name\nSIZE\n" | \
    pipenv run python3 -u -m app.main
```

**Expected output:**
```
OK
OK
Alice
1
```

---

### Test Cases

The tester will verify:

1. ✅ **Basic operations** (`s1-basic`)
   - Cache initialization
   - Storing key-value pairs
   - Retrieving existing keys
   - Handling non-existent keys (NULL)

2. ✅ **Multiple keys** (`s1-multiple-keys`)
   - Storing multiple different keys
   - Independent retrieval of each key
   - Correct SIZE after multiple operations

3. ✅ **Key updates** (`s1-update`)
   - Updating an existing key's value
   - Old value is replaced
   - SIZE doesn't increase on update

---

## Tips for Success

1. **Read the protocol carefully**
   - Commands are case-sensitive
   - Response format matters (NULL not null)
   - Line endings are important

2. **Test incrementally**
   - Test INIT first
   - Then PUT and GET
   - Finally SIZE
   - Build confidence step by step

3. **Use print for output only**
   - No logging to stderr
   - No debug messages
   - Clean stdout for testing

4. **Handle edge cases**
   - Empty cache (SIZE = 0)
   - Non-existent keys (return NULL)
   - Key updates (don't increase size)

---

## Performance Notes

### Time Complexity

- **INIT:** O(1)
- **PUT:** O(1) average case
- **GET:** O(1) average case
- **SIZE:** O(1)

### Space Complexity

- **O(n)** where n is the number of items stored

**Why O(1) for dict operations?**
- Python dict uses hash table implementation
- Average case is O(1) for lookup and insertion
- Worst case is O(n) but extremely rare

---

## Next Stage Preview

In **Stage 2**, you'll add **FIFO (First-In-First-Out) eviction**:

- Enforce capacity limits
- Evict oldest inserted item when full
- Learn about OrderedDict for insertion order tracking
- Understand the difference between FIFO and LRU

**Key difference from Stage 1:**
- Stage 1: Unlimited storage (capacity ignored)
- Stage 2: Limited storage (evict when full)

---

## Resources

- [Python dict documentation](https://docs.python.org/3/library/stdtypes.html#dict)
- [collections.OrderedDict](https://docs.python.org/3/library/collections.html#collections.OrderedDict) (for Stage 2)
- [LRU Cache on Wikipedia](https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU))

---

## Need Help?

If you're stuck:

1. Check your command parsing (use `maxsplit=2`)
2. Verify NULL vs None handling
3. Ensure SIZE is implemented
4. Test with simple manual inputs first

**Common error messages:**
- "Expected 'OK', got '...'" → Check your print statements
- "Expected 'NULL', got 'None'" → Convert None to "NULL" when printing
- "Test timed out" → Check for infinite loops or blocking input

Good luck! 🚀
