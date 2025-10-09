In this stage, you'll make your LRU cache thread-safe by adding a lock.

### Background: Why Thread Safety Matters

Real-world caches handle concurrent requests. Without thread safety, **race conditions** corrupt your data:

```python
# ❌ Race condition example
Thread 1: cache.put("a", "1")  # Updates head pointer
Thread 2: cache.put("b", "2")  # Also updates head → CRASH!
# Result: Corrupted linked list, wrong SIZE, or segfault
```

**Common race condition scenarios:**
1. **Corrupted pointers**: Two threads modify DLL simultaneously → broken links
2. **Lost updates**: Thread 1's PUT is overwritten by Thread 2
3. **Wrong SIZE**: `cache.size()` doesn't match actual entries
4. **Crash**: Accessing freed memory (especially in Go/Java)

**The solution: Locks**

```python
# ✅ With lock - operations are atomic
Thread 1: with lock: cache.put("a", "1")
Thread 2: with lock: cache.put("b", "2")  # Waits for Thread 1
```

<details>
<summary>Lock types: Exclusive vs Read-Write</summary>

**Exclusive Lock** (one at a time):
- Python: `threading.Lock`
- All operations block each other
- Simple implementation
- Good for: write-heavy workloads, Python (due to GIL)

**Read-Write Lock** (multiple readers, one writer):
- Java: `ReentrantReadWriteLock`
- Go: `sync.RWMutex`
- Multiple SIZE operations can run concurrently
- GET and PUT use write locks (modify DLL structure)
- Good for: SIZE-heavy workloads

**Performance comparison:**

| Workload | Exclusive Lock | Read-Write Lock |
|----------|----------------|-----------------|
| 90% SIZE | ~100 ops/sec | ~900 ops/sec (9x faster) |
| 50% SIZE | ~150 ops/sec | ~300 ops/sec (2x faster) |
| 90% writes | ~100 ops/sec | ~100 ops/sec (same) |

**Important for LRU Cache**: In an LRU cache, GET modifies the access order (moves node to head), so it needs a **write lock**, not a read lock. Only SIZE is truly read-only and can use a read lock. This means read-write locks have limited benefit compared to exclusive locks for typical LRU workloads.

For this stage, Python uses **exclusive lock** (simpler), Java/Go use **read-write lock** (allows concurrent SIZE operations).

</details>

---

### Requirements

To pass this stage, your program will need to:

1. Add a lock to your cache class (Python: `threading.Lock`)
2. Protect all operations with lock: GET, PUT, SIZE
3. Handle the new `CONCURRENT` command (spawns threads to test thread safety)

All operations must remain O(1) time.

---

### Tests

The tester will verify thread safety under different workload patterns:

#### Test 1: Read-heavy workload

```bash
$ echo -e "INIT 5\nPUT a 1\nPUT b 2\nCONCURRENT 10 READ_HEAVY\nGET a\nSIZE" | ./your_program.sh
OK
OK
OK
OK      # 10 threads, 70% reads, 30% writes, 1 second
1
5       # SIZE is correct
```

**What's being tested:**
- `CONCURRENT 10 READ_HEAVY` spawns 10 threads for 1 second
- 70% GET operations, 30% PUT operations
- Random keys: `key_0` to `key_99`
- Verifies: no crashes, correct SIZE, data consistency

#### Test 2: Write-heavy workload (high contention)

```bash
$ echo -e "INIT 3\nCONCURRENT 20 WRITE_HEAVY\nSIZE" | ./your_program.sh
OK
OK      # 20 threads, 90% writes, 10% reads
3       # SIZE ≤ capacity (eviction works correctly)
```

**What's being tested:**
- High write contention (20 threads, 90% writes)
- Cache capacity is enforced (SIZE never exceeds 3)
- Eviction is thread-safe
- No deadlocks or lost updates

#### Test 3: Mixed workload with evictions

```bash
$ echo -e "INIT 2\nCONCURRENT 50 MIXED\nSIZE" | ./your_program.sh
OK
OK      # 50 threads, 50% reads, 50% writes
2       # Frequent evictions, SIZE is still correct
```

**What's being tested:**
- Many threads force frequent evictions
- Small capacity (2) with high traffic
- DLL pointers remain consistent
- No race conditions during eviction

<details>
<summary>CONCURRENT command formats</summary>

```
CONCURRENT <num_threads> <workload_pattern>

Patterns:
- READ_HEAVY: 70% GET, 30% PUT
- WRITE_HEAVY: 90% PUT, 10% GET  
- MIXED: 50% GET, 50% PUT
```

Each thread runs for ~1 second on random keys (`key_0` to `key_99`).

The tester verifies:
1. No crashes or deadlocks
2. SIZE ≤ capacity
3. Data consistency (no corrupted values)
4. All threads complete successfully

</details>



---

### Notes

**Python implementation:**

```python
import threading

class LRUCache:
    def __init__(self, capacity: int):
        self.lock = threading.Lock()  # Add this
        # ... rest of init
    
    def get(self, key: str) -> str:
        with self.lock:  # Protect entire operation
            # ... your existing get logic
            return result
    
    def put(self, key: str, value: str):
        with self.lock:  # Include eviction!
            # ... your existing put logic
```

**Key points:**
- Use `with self.lock:` for GET, PUT, SIZE
- Entire operation inside lock (including eviction)
- Don't forget SIZE!

**Implementing CONCURRENT command:**

```python
# Worker function for each thread
def worker(cache, workload, duration=1.0):
    end_time = time.time() + duration
    read_prob = {"READ_HEAVY": 0.7, "WRITE_HEAVY": 0.1, "MIXED": 0.5}[workload]
    
    while time.time() < end_time:
        key = f"key_{random.randint(0, 99)}"
        if random.random() < read_prob:
            cache.get(key)
        else:
            cache.put(key, str(random.randint(0, 999)))

# Command handler
elif command == "CONCURRENT":
    num_threads, workload = int(parts[1]), parts[2]
    threads = [threading.Thread(target=worker, args=(cache, workload)) 
               for _ in range(num_threads)]
    for t in threads: t.start()
    for t in threads: t.join()
    print("OK")
```

<details>
<summary>Java implementation</summary>

```java
import java.util.concurrent.locks.ReentrantReadWriteLock;

class LRUCache {
    private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
    
    public String get(String key) {
        rwLock.writeLock().lock();  // WRITE lock - GET modifies DLL!
        try {
            if (!cache.containsKey(key)) return null;
            Node node = cache.get(key);
            moveToHead(node);  // Modifies doubly linked list structure
            return node.value;
        } finally {
            rwLock.writeLock().unlock();
        }
    }
    
    public void put(String key, String value) {
        rwLock.writeLock().lock();  // Write lock - modifies cache
        try {
            if (cache.containsKey(key)) {
                Node node = cache.get(key);
                node.value = value;
                moveToHead(node);
            } else {
                Node node = new Node(key, value);
                cache.put(key, node);
                addToHead(node);
                if (cache.size() > capacity) removeLRU();
            }
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
}
```

**Why GET needs write lock:**
- `moveToHead()` modifies the doubly linked list (updates 4+ pointers)
- Multiple concurrent GETs with read locks would corrupt the DLL
- Only SIZE can use read lock because it's truly read-only

</details>

<details>
<summary>Go implementation</summary>

```go
import "sync"

type LRUCache struct {
    mu sync.RWMutex
    // ... other fields
}

func (c *LRUCache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    // ... logic
}

func (c *LRUCache) Put(key, value string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    // ... logic (including eviction)
}

func (c *LRUCache) Size() int {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return len(c.cache)
}
```

</details>

**Common mistakes:**

**1. Forgetting to protect SIZE:**
```python
# ❌ Wrong - SIZE not protected
def size(self):
    return len(self.cache)  # Race condition!

# ✅ Correct
def size(self):
    with self.lock:
        return len(self.cache)
```

**2. Locking only part of an operation:**
```python
# ❌ Wrong - eviction outside lock
def put(self, key, value):
    with self.lock:
        self.cache[key] = value
    # Lock released here!
    if len(self.cache) > self.capacity:
        self._evict()  # Race condition: another thread could insert

# ✅ Correct - entire operation atomic
def put(self, key, value):
    with self.lock:
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self._evict()  # Still protected
```

**3. Calling locked methods from within locked methods (deadlock):**
```python
# ❌ Wrong - can deadlock with non-reentrant lock
def get(self, key):
    with self.lock:
        value = self.cache.get(key)
        if value:
            self._move_to_head(key)  # If this also tries to lock → DEADLOCK!
        return value

# ✅ Correct - helper methods don't lock (caller holds lock)
def get(self, key):
    with self.lock:
        if key in self.cache:
            node = self.cache[key]
            self._remove_node(node)  # No lock inside
            self._add_to_head(node)  # No lock inside
            return node.value
        return None
```

**4. Not unlocking in Java (missing finally):**
```java
// ❌ Wrong - lock not released if exception thrown
public void put(String key, String value) {
    writeLock.lock();
    // ... logic that might throw exception
    writeLock.unlock();  // Never reached!
}

// ✅ Correct - always unlock
public void put(String key, String value) {
    writeLock.lock();
    try {
        // ... logic
    } finally {
        writeLock.unlock();  // Always executed
    }
}
```



---

### Resources

- [Python threading.Lock](https://docs.python.org/3/library/threading.html#lock-objects)
- [Java ReentrantReadWriteLock](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/locks/ReentrantReadWriteLock.html)
- [Go sync.RWMutex](https://pkg.go.dev/sync#RWMutex)
