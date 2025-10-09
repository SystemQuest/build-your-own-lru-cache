In this stage, you'll add TTL (Time-To-Live) expiration to your cache.

```python
cache.put("session", data, ttl=30)  # Expires in 30 seconds
cache.get("session")  # Returns data (before expiration)
# ... 31 seconds later
cache.get("session")  # Returns None (expired)
```

Real caches need TTL: sessions expire, tokens refresh, DNS records have lifetimes.

<details>
<summary>Why TTL matters</summary>

Without TTL, entries stay until LRU evicts them. A session token cached for hours becomes a security risk when it should expire in 30 minutes.

**TTL vs LRU:**
- LRU: Removes least recently used when **full**
- TTL: Removes entries when **time expires** (even if not full)

**Lazy deletion** (this stage):
- Check expiration during GET
- Simple, no background threads
- Expired entries stay in memory until accessed

</details>

### Requirements

Your cache needs to:

1. **Store expiration time with each entry**
   - Add `expire_at` field to Node (Unix timestamp or None)
   - Calculate: `expire_at = time.time() + ttl`

2. **Check expiration in GET** (lazy deletion)
   - If `time.time() >= node.expire_at`, remove entry and return None
   - Otherwise return value and move to head

3. **Support optional TTL in PUT**
   ```bash
   PUT key value        # No expiration
   PUT key value 30     # Expires in 30 seconds
   ```

4. **Implement SLEEP command** (for testing)
   ```python
   time.sleep(float(parts[1]))
   ```

All operations remain O(1). Expiration checks happen inside locks (atomic).

### Tests

#### Test 1: Basic expiration

```bash
$ echo -e "INIT 5\nPUT a 1 1\nGET a\nSLEEP 1.5\nGET a\nSIZE" | ./your_program.sh
OK
OK
1       # Not expired yet
OK
NULL    # Expired and removed
0
```

#### Test 2: Multiple TTLs

```bash
$ echo -e "INIT 5\nPUT short 1 1\nPUT long 2 10\nSLEEP 1.5\nGET short\nGET long\nSIZE" | ./your_program.sh
OK
OK
OK
OK
NULL    # Expired
2       # Still valid
1
```

#### Test 3: TTL with LRU eviction

```bash
$ echo -e "INIT 2\nPUT a 1 10\nPUT b 2 10\nPUT c 3\nGET a" | ./your_program.sh
OK
OK
OK
OK      # 'c' evicts 'a' by LRU (not expiration)
NULL    # Evicted by LRU
```

<details>
<summary>All test cases (9 total)</summary>

The tester runs these scenarios:
- `xy7`: Basic TTL expiration
- `xy7-immediate`: Access before expiration
- `xy7-multiple`: Different TTLs expire independently
- `xy7-eviction`: LRU eviction works with TTL entries
- `xy7-no-expiration`: Entries without TTL never expire
- `xy7-mixed`: Mix of TTL and non-TTL entries
- `xy7-update`: PUT updates existing entry's TTL
- `xy7-size`: SIZE consistent after expiration
- `xy7-concurrent`: Thread safety with TTL

</details>

### Notes

<details>
<summary>Python implementation</summary>

```python
import time

class Node:
    def __init__(self, key: str, value: str, expire_at: float = None):
        self.key = key
        self.value = value
        self.expire_at = expire_at  # None = no expiration
        self.prev = None
        self.next = None

def get(self, key: str) -> str | None:
    with self.lock:
        if key not in self.cache:
            return None
        
        node = self.cache[key]
        
        # Lazy deletion: check expiration
        if node.expire_at and time.time() >= node.expire_at:
            self._remove_node(node)
            del self.cache[key]
            return None
        
        self._move_to_head(node)
        return node.value

def put(self, key: str, value: str, ttl: int = None):
    with self.lock:
        expire_at = time.time() + ttl if ttl else None
        
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            node.expire_at = expire_at  # Update TTL
            self._move_to_head(node)
        else:
            node = Node(key, value, expire_at)
            self.cache[key] = node
            self._add_to_head(node)
            if len(self.cache) > self.capacity:
                self._remove_lru()

# Command parsing
elif command == "PUT":
    key, value = parts[1], parts[2]
    ttl = int(parts[3]) if len(parts) > 3 else None
    cache.put(key, value, ttl)
    print("OK")

elif command == "SLEEP":
    time.sleep(float(parts[1]))
    print("OK")
```

</details>

<details>
<summary>Java implementation</summary>

```java
class Node {
    String key, value;
    Long expireAt;  // milliseconds, null = no expiration
    Node prev, next;
}

public String get(String key) {
    rwLock.writeLock().lock();  // WRITE lock - removes expired entries + moves node
    try {
        if (!cache.containsKey(key)) return null;
        
        Node node = cache.get(key);
        
        // Lazy deletion - removes expired entry
        if (node.expireAt != null && System.currentTimeMillis() >= node.expireAt) {
            removeNode(node);
            cache.remove(key);
            return null;
        }
        
        moveToHead(node);  // Modifies DLL
        return node.value;
    } finally {
        rwLock.writeLock().unlock();
    }
}

public void put(String key, String value, Integer ttlSeconds) {
    rwLock.writeLock().lock();  // Write lock - modifies cache
    try {
        Long expireAt = ttlSeconds != null 
            ? System.currentTimeMillis() + (ttlSeconds * 1000L)
            : null;
        
        // ... update or create node with expireAt
    } finally {
        rwLock.writeLock().unlock();
    }
}

public int size() {
    rwLock.readLock().lock();  // READ lock - only reads, doesn't modify
    try {
        return cache.size();
    } finally {
        rwLock.readLock().unlock();
    }
}
```

**Why GET needs write lock in Stage 6:**
- Removes expired entries (modifies HashMap and DLL)
- Moves accessed node to head (modifies DLL)
- Only SIZE can use read lock (truly read-only)

```
```

</details>

<details>
<summary>Go implementation</summary>

```go
import "time"

type Node struct {
    key, value string
    expireAt   *time.Time  // nil = no expiration
    prev, next *Node
}

func (c *LRUCache) Get(key string) (string, bool) {
    c.mu.Lock()  // Might delete expired entry
    defer c.mu.Unlock()
    
    node, exists := c.cache[key]
    if !exists {
        return "", false
    }
    
    // Lazy deletion
    if node.expireAt != nil && time.Now().After(*node.expireAt) {
        c.removeNode(node)
        delete(c.cache, key)
        return "", false
    }
    
    c.moveToHead(node)
    return node.value, true
}

func (c *LRUCache) Put(key, value string, ttlSeconds *int) {
    c.mu.Lock()
    defer c.mu.Unlock()
    
    var expireAt *time.Time
    if ttlSeconds != nil {
        t := time.Now().Add(time.Duration(*ttlSeconds) * time.Second)
        expireAt = &t
    }
    
    // ... update or create node with expireAt
}
```

</details>

<details>
<summary>Common mistakes</summary>

**Not checking expiration:**
```python
# ❌ Expired entries never removed
def get(self, key):
    return self.cache.get(key).value

# ✅ Check expiration in GET
if node.expire_at and time.time() >= node.expire_at:
    self._remove_node(node)
    del self.cache[key]
    return None
```

**Not updating TTL on PUT:**
```python
# ❌ Forgot to update TTL
node.value = value  # Missing: node.expire_at = expire_at

# ✅ Update both value and TTL
node.value = value
node.expire_at = expire_at
```

**Checking expiration outside lock:**
```python
# ❌ Race condition
if node.expire_at and time.time() >= node.expire_at:
    with self.lock:  # Too late!
        del self.cache[key]

# ✅ Entire check inside lock
with self.lock:
    if node.expire_at and time.time() >= node.expire_at:
        del self.cache[key]
```

</details>

### Resources

- [Python time.time()](https://docs.python.org/3/library/time.html) - Unix timestamp
- [Java System.currentTimeMillis()](https://docs.oracle.com/javase/8/docs/api/java/lang/System.html#currentTimeMillis--) - Timestamp in milliseconds
- [Go time.Now()](https://pkg.go.dev/time#Now) - Current time
- [Redis EXPIRE](https://redis.io/commands/expire/) - How Redis implements TTL
