In this stage, you'll implement a basic key-value cache with `GET`, `PUT`, and `SIZE` operations.

This is the foundation for all future stages - a simple in-memory store with O(1) lookups.

### Basic Cache Operations

<details>
<summary>Background: What is a cache?</summary>

A **cache** is a fast, in-memory key-value store that sits between your application and slower storage (database, disk, network).

**Key concepts:**
- **Key-value store**: Maps keys to values (like a dictionary/hash map)
- **O(1) operations**: Lookups and inserts are constant time
- **Capacity-limited**: Fixed maximum size (enforced in Stage 2+)

**Common use cases:**
- Web applications: Store frequently accessed data (user sessions, API responses)
- Databases: Cache query results to reduce load
- Operating systems: Cache disk blocks in memory

**In this stage:**
- No capacity enforcement (unlimited storage)
- Simple dictionary-based implementation
- Focus on correct command handling

</details>

---

### Implementation Requirements

To pass this stage, your program will need to:

1. **Read commands from stdin** and write responses to stdout
   - Commands are line-separated
   - Parse command format correctly
   
2. **Implement 4 commands:**
   - `INIT <capacity>` - Initialize cache
   - `PUT <key> <value>` - Store or update key-value pair
   - `GET <key>` - Retrieve value (return `NULL` if not found)
   - `SIZE` - Return current number of items
   
3. **Use a hash map/dictionary** for O(1) operations
   - Python: `dict`
   - Java: `HashMap`
   - Go: `map`

**Note:** In Stage 1, capacity is stored but not enforced. Eviction logic comes in Stage 2.

---

### Tests

The tester will execute your program like this:

```bash
$ ./your_program.sh
```

It will then send commands via stdin. **The tester runs 3 test scenarios** to verify basic cache operations.

#### Test 1: Basic operations

```bash
$ echo -e "INIT 10\nPUT name Alice\nGET name\nGET age\nPUT name Bob\nGET name" | ./your_program.sh
OK
OK
Alice
NULL    # 'age' doesn't exist
OK
Bob     # 'name' updated to Bob
```

**Expected behavior:**
- `INIT` returns `OK`
- `PUT` stores key-value pairs and returns `OK`
- `GET` returns the value if key exists, `NULL` if not
- Updating an existing key replaces the old value

#### Test 2: Multiple keys

```bash
$ echo -e "INIT 5\nPUT key1 value1\nPUT key2 value2\nPUT key3 value3\nGET key1\nGET key2\nGET key3\nGET key4" | ./your_program.sh
OK
OK
OK
OK
value1
value2
value3
NULL    # 'key4' doesn't exist
```

**Expected behavior:**
- Cache handles multiple independent keys
- Each key retrieves its own value
- Non-existent keys return `NULL`

#### Test 3: Key updates

```bash
$ echo -e "INIT 10\nPUT name Alice\nGET name\nPUT name Bob\nGET name\nPUT name Charlie\nGET name" | ./your_program.sh
OK
OK
Alice
OK
Bob      # Updated
OK
Charlie  # Updated again
```

**Expected behavior:**
- Updating an existing key replaces its value
- No error or special handling needed for updates

---

### Notes

<details>
<summary>Simple implementation with dict</summary>

Python's built-in `dict` is perfect for Stage 1:

```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # Simple dict for O(1) lookup
    
    def get(self, key: str) -> str | None:
        """Retrieve value by key, return None if not found"""
        return self.cache.get(key)
    
    def put(self, key: str, value: str) -> None:
        """Store or update key-value pair"""
        self.cache[key] = value  # Dict handles both insert and update
    
    def size(self) -> int:
        """Return current cache size"""
        return len(self.cache)
```

**Why dict?**
- O(1) average-case lookup and insertion
- Automatic handling of updates (no manual check needed)
- Built-in, no dependencies

</details>

<details>
<summary>Command parsing</summary>

Read commands line by line from stdin:

```python
import sys

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
        key = parts[1]
        value = parts[2]
        cache.put(key, value)
        print("OK")
    
    elif command == "GET":
        key = parts[1]
        result = cache.get(key)
        if result is None:
            print("NULL")  # ← Important: print "NULL", not "None"
        else:
            print(result)
    
    elif command == "SIZE":
        print(cache.size())
```

**Key points:**
- Use `line.split()` to parse commands
- Print exactly `"NULL"` for non-existent keys (not `"None"` or empty string)
- Initialize cache on `INIT` command (not at module level)

</details>

<details>
<summary>Common pitfalls</summary>

**1. Returning wrong value for missing keys**
```python
# ❌ WRONG - prints "None" instead of "NULL"
result = cache.get(key)
print(result)  # Prints "None" for missing keys

# ✅ CORRECT - prints "NULL"
result = cache.get(key)
if result is None:
    print("NULL")
else:
    print(result)
```

**2. Not handling updates correctly**
```python
# ❌ WRONG - doesn't update existing keys
def put(self, key, value):
    if key not in self.cache:
        self.cache[key] = value  # Only adds new keys!

# ✅ CORRECT - dict handles both insert and update
def put(self, key, value):
    self.cache[key] = value  # Works for both new and existing keys
```

**3. Initializing cache at wrong time**
```python
# ❌ WRONG - creates cache before INIT command
cache = LRUCache(10)  # At module level

for line in sys.stdin:
    # ...

# ✅ CORRECT - create cache on INIT command
cache = None

for line in sys.stdin:
    if command == "INIT":
        cache = LRUCache(capacity)
```

**4. Not implementing SIZE**
```python
# ❌ WRONG - SIZE not implemented
elif command == "SIZE":
    print("0")  # Always returns 0

# ✅ CORRECT - return actual size
elif command == "SIZE":
    print(len(self.cache))
```

</details>

<details>
<summary>Why O(1) for dict operations?</summary>

Python's `dict` uses a hash table internally:

```
Key → hash(key) → bucket index → value

Example:
"name" → hash("name") = 12345 → bucket[5] → "Alice"
```

**Time complexity:**
- `get(key)`: O(1) average, O(n) worst case (hash collisions, very rare)
- `put(key, value)`: O(1) average, O(n) worst case
- `len(dict)`: O(1) (Python tracks size internally)

**Space complexity:**
- O(n) where n is the number of items stored

**Why worst case is rare:**
- Python uses a good hash function
- Hash table is resized when load factor is too high
- Collisions are handled with open addressing

In practice, dict operations are effectively O(1).

</details>

---

### Resources

- [Python dict documentation](https://docs.python.org/3/library/stdtypes.html#dict) - Official dict reference
- [Hash table (Wikipedia)](https://en.wikipedia.org/wiki/Hash_table) - Theory behind dict implementation
- [Big O notation](https://en.wikipedia.org/wiki/Big_O_notation) - Understanding O(1), O(n), etc.
