In this stage, you'll add Time-To-Live (TTL) expiration to your cache entries.

This enables automatic cleanup of stale data - a critical feature for production caches where entries have natural lifetimes (sessions, API tokens, computed results).

### TTL Expiration

<details>
<summary>Background: Why TTL matters</summary>

Without TTL, cached data stays forever (until evicted by LRU). This causes problems:

```python
# Cache without TTL:
cache.put("session:abc", user_data)  # Stays until evicted by LRU
# Problem: Session expires in 30 minutes, but cache keeps it for hours!

# Cache with TTL:
cache.put("session:abc", user_data, ttl=1800)  # Expires in 30 minutes
# After 30 min: GET returns None (expired)
```

**Real-world scenarios:**
- **Sessions**: Expire after 30 minutes of inactivity
- **API tokens**: Refresh tokens expire after 1 hour
- **Computed results**: Cache expensive calculations for 5 minutes
- **Rate limiting**: Track API calls per minute/hour
- **DNS records**: Cache DNS lookups with their original TTL

**TTL vs LRU:**
```
LRU eviction: Removes least recently used when cache is FULL
TTL expiration: Removes entries when TIME expires (even if cache not full)

Both can happen:
1. Entry expires (TTL) → GET returns None
2. Entry evicted (LRU) → GET returns None
3. Entry valid → GET returns value
```

**Two cleanup strategies:**

1. **Lazy deletion** (on access):
   - Check expiration when GET is called
   - Simple and efficient
   - Dead entries stay in memory until accessed

2. **Active cleanup** (background):
   - Periodic scan to remove expired entries
   - Frees memory proactively
   - More complex (needs background thread)

</details>

---

### Implementation Requirements

To pass this stage, your program will need to:

1. **Extend PUT to accept TTL** (in seconds)
   ```python
   def put(self, key: str, value: str, ttl: int = None) -> None:
       # Store value with expiration time
       expire_at = time.time() + ttl if ttl else None
       # ... existing put logic
   ```

2. **Check expiration in GET**
   ```python
   def get(self, key: str) -> str | None:
       with self.lock:
           if key not in self.cache:
               return None
           
           node = self.cache[key]
           
           # Check if expired (lazy deletion)
           if node.expire_at and time.time() >= node.expire_at:
               self._remove_expired(key)  # Delete expired entry
               return None
           
           # Not expired - return value
           self._move_to_head(node)
           return node.value
   ```

3. **Support PUT command with optional TTL**
   ```bash
   PUT key value        # No TTL (never expires)
   PUT key value 30     # Expires in 30 seconds
   ```

4. **Maintain thread safety**
   - All TTL operations must be protected by locks
   - Expiration checks are atomic with get/put operations

**Complexity remains O(1) for all operations.**

---

### Tests

The tester will execute your program like this:

```bash
$ ./your_program.sh
```

It will test TTL expiration with various scenarios.

Below are 3 example test scenarios (the actual test suite includes additional tests for edge cases and concurrent TTL):

#### Test 1: Basic TTL expiration

```bash
$ echo -e "INIT 5\nPUT a 1 1\nGET a\nSLEEP 1.5\nGET a\nSIZE" | ./your_program.sh
OK      # INIT 5
OK      # PUT a 1 1 (TTL = 1 second)
1       # GET a (immediately, not expired yet)
OK      # SLEEP 1.5 seconds
NULL    # GET a (expired after 1 second)
0       # SIZE (expired entry was removed)
```

**Expected behavior:**
- `PUT a 1 1` stores value "1" with TTL of 1 second
- First `GET a` returns "1" (not expired yet)
- After `SLEEP 1.5`, the entry expires
- Second `GET a` returns NULL and removes the expired entry
- `SIZE` is 0 (expired entry was deleted)

#### Test 2: TTL with eviction

```bash
$ echo -e "INIT 2\nPUT a 1 10\nPUT b 2 10\nPUT c 3\nGET a\nGET c\nSIZE" | ./your_program.sh
OK      # INIT 2
OK      # PUT a 1 10 (TTL = 10 seconds)
OK      # PUT b 2 10 (TTL = 10 seconds)
OK      # PUT c 3 (no TTL, causes LRU eviction)
NULL    # GET a (evicted by LRU, not expired)
3       # GET c (most recent)
2       # SIZE
```

**Expected behavior:**
- Cache capacity is 2
- First two PUTs fill the cache (both with 10-second TTL)
- Third PUT evicts "a" by LRU (least recently used)
- `GET a` returns NULL (evicted, not because expired)
- Eviction happens before expiration (LRU takes priority)

#### Test 3: Multiple entries with different TTLs

```bash
$ echo -e "INIT 5\nPUT short 1 1\nPUT medium 2 3\nPUT long 3 10\nSLEEP 1.5\nGET short\nGET medium\nGET long\nSIZE" | ./your_program.sh
OK      # INIT 5
OK      # PUT short with TTL=1
OK      # PUT medium with TTL=3
OK      # PUT long with TTL=10
OK      # SLEEP 1.5 seconds
NULL    # GET short (expired after 1 second)
2       # GET medium (still valid, expires at 3 seconds)
3       # GET long (still valid, expires at 10 seconds)
2       # SIZE (only medium and long remain)
```

**Expected behavior:**
- Three entries with different TTLs (1s, 3s, 10s)
- After 1.5 seconds, only "short" expires
- `GET short` returns NULL and removes it
- Other entries are still valid
- SIZE correctly reflects only non-expired entries

---

### Notes

<details>
<summary>SLEEP command</summary>

The `SLEEP` command pauses execution to test TTL expiration:

```
SLEEP <seconds>

Examples:
SLEEP 1      # Sleep for 1 second
SLEEP 1.5    # Sleep for 1.5 seconds
SLEEP 0.1    # Sleep for 0.1 seconds (100ms)
```

The tester uses this to simulate time passing and verify expiration works correctly.

**Implementation:**
```python
elif command == "SLEEP":
    duration = float(parts[1])
    time.sleep(duration)
    print("OK")
```

</details>

<details>
<summary>Python implementation with TTL</summary>

```python
import time
import threading

class Node:
    def __init__(self, key: str, value: str, expire_at: float = None):
        self.key = key
        self.value = value
        self.expire_at = expire_at  # Unix timestamp when entry expires (None = no expiration)
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.lock = threading.Lock()
        # ... rest of initialization
    
    def get(self, key: str) -> str | None:
        with self.lock:
            if key not in self.cache:
                return None
            
            node = self.cache[key]
            
            # Check if expired (lazy deletion)
            if node.expire_at is not None and time.time() >= node.expire_at:
                self._remove_expired(key)
                return None
            
            # Not expired - move to head and return
            self._move_to_head(node)
            return node.value
    
    def put(self, key: str, value: str, ttl: int = None) -> None:
        with self.lock:
            # Calculate expiration time
            expire_at = time.time() + ttl if ttl is not None else None
            
            if key in self.cache:
                # Update existing entry
                node = self.cache[key]
                node.value = value
                node.expire_at = expire_at  # Update TTL
                self._move_to_head(node)
            else:
                # Create new entry
                node = Node(key, value, expire_at)
                self.cache[key] = node
                self._add_to_head(node)
                
                # Evict LRU if over capacity
                if len(self.cache) > self.capacity:
                    self._remove_lru()
    
    def _remove_expired(self, key: str) -> None:
        """Remove expired entry from cache (called from get)"""
        node = self.cache[key]
        self._remove_node(node)
        del self.cache[key]
    
    # ... rest of methods (size, _remove_node, _add_to_head, etc.)
```

**Key points:**
- `Node` stores `expire_at` (Unix timestamp, None = no expiration)
- `get()` checks expiration and deletes if expired
- `put()` accepts optional `ttl` parameter (in seconds)
- Expiration check is inside the lock (atomic with get operation)
- Expired entries are removed lazily (only when accessed)

**Command parsing:**
```python
elif command == "PUT":
    key = parts[1]
    value = parts[2]
    ttl = int(parts[3]) if len(parts) > 3 else None
    cache.put(key, value, ttl)
    print("OK")
```

</details>

<details>
<summary>Java implementation with TTL</summary>

```java
import java.util.HashMap;
import java.util.concurrent.locks.ReentrantReadWriteLock;

class Node {
    String key;
    String value;
    Long expireAt;  // Unix timestamp in milliseconds (null = no expiration)
    Node prev;
    Node next;
    
    Node(String key, String value, Long expireAt) {
        this.key = key;
        this.value = value;
        this.expireAt = expireAt;
    }
}

class LRUCache {
    private final int capacity;
    private final HashMap<String, Node> cache;
    private final ReentrantReadWriteLock rwLock;
    private final ReentrantReadWriteLock.ReadLock readLock;
    private final ReentrantReadWriteLock.WriteLock writeLock;
    // ... head, tail fields
    
    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new HashMap<>();
        this.rwLock = new ReentrantReadWriteLock();
        this.readLock = rwLock.readLock();
        this.writeLock = rwLock.writeLock();
        // ... initialize head, tail
    }
    
    public String get(String key) {
        writeLock.lock();  // Need write lock because we might delete expired entry
        try {
            if (!cache.containsKey(key)) {
                return null;
            }
            
            Node node = cache.get(key);
            
            // Check if expired (lazy deletion)
            if (node.expireAt != null && System.currentTimeMillis() >= node.expireAt) {
                removeExpired(key);
                return null;
            }
            
            // Not expired - move to head and return
            moveToHead(node);
            return node.value;
        } finally {
            writeLock.unlock();
        }
    }
    
    public void put(String key, String value, Integer ttlSeconds) {
        writeLock.lock();
        try {
            // Calculate expiration time
            Long expireAt = ttlSeconds != null 
                ? System.currentTimeMillis() + (ttlSeconds * 1000L)
                : null;
            
            if (cache.containsKey(key)) {
                Node node = cache.get(key);
                node.value = value;
                node.expireAt = expireAt;
                moveToHead(node);
            } else {
                Node node = new Node(key, value, expireAt);
                cache.put(key, node);
                addToHead(node);
                
                if (cache.size() > capacity) {
                    removeLRU();
                }
            }
        } finally {
            writeLock.unlock();
        }
    }
    
    private void removeExpired(String key) {
        Node node = cache.get(key);
        removeNode(node);
        cache.remove(key);
    }
    
    // ... rest of methods
}
```

**Key points:**
- `Node` stores `expireAt` in milliseconds (null = no expiration)
- `get()` uses **write lock** (might delete expired entry)
- `put()` accepts optional `ttlSeconds` parameter
- `System.currentTimeMillis()` for Unix timestamp

**Command parsing:**
```java
String[] parts = line.split(" ");
String command = parts[0];

if (command.equals("PUT")) {
    String key = parts[1];
    String value = parts[2];
    Integer ttl = parts.length > 3 ? Integer.parseInt(parts[3]) : null;
    cache.put(key, value, ttl);
    System.out.println("OK");
}
```

</details>

<details>
<summary>Go implementation with TTL</summary>

```go
import (
    "sync"
    "time"
)

type Node struct {
    key      string
    value    string
    expireAt *time.Time  // nil = no expiration
    prev     *Node
    next     *Node
}

type LRUCache struct {
    capacity int
    cache    map[string]*Node
    mu       sync.RWMutex
    head     *Node
    tail     *Node
}

func NewLRUCache(capacity int) *LRUCache {
    // ... initialization
}

func (c *LRUCache) Get(key string) (string, bool) {
    c.mu.Lock()  // Need exclusive lock (might delete expired entry)
    defer c.mu.Unlock()
    
    node, exists := c.cache[key]
    if !exists {
        return "", false
    }
    
    // Check if expired (lazy deletion)
    if node.expireAt != nil && time.Now().After(*node.expireAt) {
        c.removeExpired(key)
        return "", false
    }
    
    // Not expired - move to head and return
    c.moveToHead(node)
    return node.value, true
}

func (c *LRUCache) Put(key string, value string, ttlSeconds *int) {
    c.mu.Lock()
    defer c.mu.Unlock()
    
    // Calculate expiration time
    var expireAt *time.Time
    if ttlSeconds != nil {
        t := time.Now().Add(time.Duration(*ttlSeconds) * time.Second)
        expireAt = &t
    }
    
    if node, exists := c.cache[key]; exists {
        node.value = value
        node.expireAt = expireAt
        c.moveToHead(node)
    } else {
        node := &Node{
            key:      key,
            value:    value,
            expireAt: expireAt,
        }
        c.cache[key] = node
        c.addToHead(node)
        
        if len(c.cache) > c.capacity {
            c.removeLRU()
        }
    }
}

func (c *LRUCache) removeExpired(key string) {
    node := c.cache[key]
    c.removeNode(node)
    delete(c.cache, key)
}

// ... rest of methods
```

**Key points:**
- `Node` stores `expireAt` as `*time.Time` (nil = no expiration)
- `Get()` uses **exclusive lock** (might delete expired entry)
- `Put()` accepts optional `ttlSeconds` pointer
- `time.Now()` for current time

**Command parsing:**
```go
parts := strings.Fields(line)
command := parts[0]

if command == "PUT" {
    key := parts[1]
    value := parts[2]
    var ttl *int
    if len(parts) > 3 {
        t, _ := strconv.Atoi(parts[3])
        ttl = &t
    }
    cache.Put(key, value, ttl)
    fmt.Println("OK")
}
```

</details>

<details>
<summary>Common pitfalls</summary>

**1. Forgetting to check expiration in GET**
```python
# ❌ WRONG - expired entries are never removed
def get(self, key):
    with self.lock:
        if key in self.cache:
            return self.cache[key].value
        return None

# ✅ CORRECT - check expiration before returning
def get(self, key):
    with self.lock:
        if key in self.cache:
            node = self.cache[key]
            if node.expire_at and time.time() >= node.expire_at:
                self._remove_expired(key)
                return None
            return node.value
        return None
```

**2. Not updating TTL on PUT update**
```python
# ❌ WRONG - TTL not updated when key already exists
def put(self, key, value, ttl=None):
    if key in self.cache:
        node = self.cache[key]
        node.value = value  # Updated value but not TTL!
        
# ✅ CORRECT - update TTL as well
def put(self, key, value, ttl=None):
    expire_at = time.time() + ttl if ttl else None
    if key in self.cache:
        node = self.cache[key]
        node.value = value
        node.expire_at = expire_at  # Update TTL
```

**3. Using wrong time units**
```python
# ❌ WRONG - mixing seconds and milliseconds
expire_at = time.time() * 1000 + ttl  # time.time() is already in seconds!

# ✅ CORRECT - consistent units (seconds)
expire_at = time.time() + ttl  # Both in seconds
```

**4. Not protecting expiration check with lock**
```python
# ❌ WRONG - race condition (check outside lock)
if key in self.cache:
    node = self.cache[key]
    if node.expire_at and time.time() >= node.expire_at:
        # Time passes here! Another thread might access node
        with self.lock:
            self._remove_expired(key)  # Too late!

# ✅ CORRECT - entire check inside lock
with self.lock:
    if key in self.cache:
        node = self.cache[key]
        if node.expire_at and time.time() >= node.expire_at:
            self._remove_expired(key)
            return None
```

**5. Expiration precision issues**
```python
# ❌ WRONG - >= comparison can miss exact expiration time
if time.time() >= node.expire_at:  # What if time.time() == expire_at exactly?

# ✅ CORRECT - use >= for simplicity (entry expired AT the time)
if time.time() >= node.expire_at:  # Expired at or after expiration time
```

**6. Forgetting SIZE should exclude expired entries**
```python
# ❌ WRONG - SIZE includes expired entries
def size(self):
    return len(self.cache)

# ⚠️ ACCEPTABLE for this stage - lazy deletion means expired entries
# stay until accessed. SIZE reflects actual memory usage.
# Active cleanup (Stage 7) will fix this.
def size(self):
    with self.lock:
        return len(self.cache)  # Includes expired entries
```

</details>

<details>
<summary>Testing TTL locally</summary>

You can test TTL manually before submitting:

**Python:**
```python
import time

cache = LRUCache(5)

# Test basic expiration
cache.put("a", "1", ttl=1)
print(cache.get("a"))  # Should print: 1
time.sleep(1.5)
print(cache.get("a"))  # Should print: None (expired)
print(cache.size())    # Should print: 0 (expired entry removed)

# Test multiple TTLs
cache.put("short", "1", ttl=1)
cache.put("long", "2", ttl=10)
time.sleep(1.5)
print(cache.get("short"))  # None (expired)
print(cache.get("long"))   # 2 (still valid)
print(cache.size())        # 1 (only long remains)
```

**Java:**
```java
LRUCache cache = new LRUCache(5);

// Test basic expiration
cache.put("a", "1", 1);  // 1 second TTL
System.out.println(cache.get("a"));  // 1
Thread.sleep(1500);
System.out.println(cache.get("a"));  // null (expired)
System.out.println(cache.size());    // 0

// Test multiple TTLs
cache.put("short", "1", 1);
cache.put("long", "2", 10);
Thread.sleep(1500);
System.out.println(cache.get("short"));  // null
System.out.println(cache.get("long"));   // 2
System.out.println(cache.size());        // 1
```

**Go:**
```go
cache := NewLRUCache(5)

// Test basic expiration
ttl1 := 1
cache.Put("a", "1", &ttl1)
fmt.Println(cache.Get("a"))  // 1, true
time.Sleep(1500 * time.Millisecond)
fmt.Println(cache.Get("a"))  // "", false (expired)
fmt.Println(cache.Size())    // 0

// Test multiple TTLs
ttlShort := 1
ttlLong := 10
cache.Put("short", "1", &ttlShort)
cache.Put("long", "2", &ttlLong)
time.Sleep(1500 * time.Millisecond)
fmt.Println(cache.Get("short"))  // "", false
fmt.Println(cache.Get("long"))   // "2", true
fmt.Println(cache.Size())        // 1
```

If expired entries return values instead of None/null, you have a bug in expiration checking.

</details>

<details>
<summary>Design considerations</summary>

**Lazy deletion vs Active cleanup:**

| Approach | Pros | Cons | This Stage |
|----------|------|------|------------|
| **Lazy deletion** | Simple, no background thread, efficient | Dead entries waste memory until accessed | ✅ Implement this |
| **Active cleanup** | Proactive memory cleanup, better for many expired entries | Complex (background thread), overhead | ❌ Stage 7 |

**Why lazy deletion first?**
- Simpler implementation (no background threads)
- No concurrency complexity (just check on access)
- Works well for moderate expiration rates
- Foundation for active cleanup later

**When does lazy deletion work well?**
- Entries are accessed frequently (expired ones get cleaned up)
- Cache hit rate is high
- Memory is not extremely tight

**When do you need active cleanup?**
- Many entries expire without being accessed
- Memory is constrained
- Need guaranteed cleanup timing
- Cache miss rate is high

**TTL and thread safety:**
- Expiration check must be atomic with GET operation
- Can't check outside lock (race condition)
- For Java: GET needs **write lock** (might delete)
- For Go: GET needs **exclusive lock** (might delete)
- For Python: Exclusive lock already used

</details>

<details>
<summary>Performance considerations</summary>

**Time complexity:**
```
GET: O(1) - HashMap lookup + expiration check + potential deletion
PUT: O(1) - HashMap insert + DLL update + TTL calculation
SIZE: O(1) - Return HashMap size
```

All operations remain O(1) despite TTL checking.

**Memory overhead:**
```
Without TTL: Node = key + value + 2 pointers (prev/next)
With TTL:    Node = key + value + 2 pointers + 1 timestamp (8 bytes)

Memory increase: ~8 bytes per entry (negligible)
```

**Lazy deletion efficiency:**

Best case (high hit rate):
- Expired entries are accessed and cleaned up quickly
- Memory waste is minimal

Worst case (low hit rate):
- Many expired entries never accessed
- They stay in memory until LRU eviction
- Can waste significant memory

**Solution: Active cleanup (Stage 7)**
- Background thread periodically scans for expired entries
- Guarantees cleanup even if entries not accessed
- Keeps memory usage under control

</details>

---

### Resources

- [Time-To-Live (Wikipedia)](https://en.wikipedia.org/wiki/Time_to_live) - TTL concept overview
- [Python time module](https://docs.python.org/3/library/time.html) - time.time() and sleep()
- [Java System.currentTimeMillis()](https://docs.oracle.com/javase/8/docs/api/java/lang/System.html#currentTimeMillis--) - Current time in milliseconds
- [Go time package](https://pkg.go.dev/time) - Time operations in Go
- [Redis TTL](https://redis.io/commands/ttl/) - How Redis implements TTL
- [Lazy deletion vs Active cleanup](https://en.wikipedia.org/wiki/Cache_replacement_policies#Time_aware_least_recently_used_(TLRU)) - Deletion strategies
