In this stage, you'll make your LRU cache thread-safe to handle concurrent operations.

This is the first step toward production-grade caching - real applications have multiple threads/goroutines accessing the cache simultaneously.

### Thread Safety

<details>
<summary>Background: Why thread safety matters</summary>

Without thread safety, concurrent operations cause **race conditions**:

```python
# Two threads run simultaneously:
Thread 1: cache.get("user:123")
Thread 2: cache.put("user:456", data)

# Race condition examples:
1. Corrupted internal state (broken DLL pointers)
2. Lost updates (one PUT overwrites another)
3. Inconsistent SIZE (cache.size() doesn't match reality)
4. Crash (accessing freed memory in Go/Java)
```

**Real-world scenarios:**
- Web server: Multiple requests access cache concurrently
- Background jobs: Worker threads update cache while web handlers read
- Microservices: Shared cache across multiple service instances

**The solution: Locks**

```
Lock types:
┌──────────────┬────────────┬────────────┐
│ Operation    │ Lock Type  │ Why?       │
├──────────────┼────────────┼────────────┤
│ GET (read)   │ Read lock  │ Multiple OK│
│ PUT (write)  │ Write lock │ Exclusive  │
│ SIZE (read)  │ Read lock  │ Multiple OK│
└──────────────┴────────────┴────────────┘
```

**Read-Write Lock benefits:**
- Multiple threads can read concurrently (no blocking)
- Write operations are exclusive (prevents corruption)
- Much better performance than exclusive locks for read-heavy workloads

</details>

---

### Implementation Requirements

To pass this stage, your program will need to:

1. **Add a lock** to your cache class
   - Python: `threading.Lock` (exclusive lock - sufficient for this stage)
   - Java: `ReentrantReadWriteLock` (read-write lock - better for read-heavy workloads)
   - Go: `sync.RWMutex` (read-write lock - better for read-heavy workloads)

2. **Protect GET operations** with lock
   ```python
   def get(self, key):
       with self.lock:
           # ... existing get logic
   ```

3. **Protect PUT operations** with lock
   ```python
   def put(self, key, value):
       with self.lock:
           # ... existing put logic (including eviction)
   ```

4. **Protect SIZE operations** with lock
   ```python
   def size(self):
       with self.lock:
           return len(self.cache)
   ```

**All operations must remain O(1) with minimal lock contention.**

---

### Tests

The tester will execute your program like this:

```bash
$ ./your_program.sh
```

It will then send a new command `CONCURRENT` to run concurrent operations. **The tester will verify thread safety** under different workload patterns.

Below are 3 example test scenarios (the actual test suite includes additional tests for edge cases and stress scenarios):

#### Test 1: Concurrent reads and writes

```bash
$ echo -e "INIT 5\nPUT a 1\nPUT b 2\nPUT c 3\nCONCURRENT 10 READ_HEAVY\nGET a\nGET b\nGET c\nSIZE" | ./your_program.sh
OK
OK
OK
OK
OK      # CONCURRENT spawns 10 threads: 70% reads, 30% writes
1       # All values are consistent
2
3
5       # SIZE is correct (no lost updates)
```

**Expected behavior:**
- `CONCURRENT 10 READ_HEAVY` spawns 10 threads running for 1 second
- Threads perform: 70% GET operations, 30% PUT operations
- After concurrent operations, all data is consistent
- No corrupted pointers, no crashes

#### Test 2: Concurrent writes (high contention)

```bash
$ echo -e "INIT 3\nCONCURRENT 20 WRITE_HEAVY\nSIZE" | ./your_program.sh
OK
OK      # CONCURRENT spawns 20 threads: 90% writes, 10% reads
3       # SIZE is exactly 3 (capacity enforced correctly)
```

**Expected behavior:**
- `CONCURRENT 20 WRITE_HEAVY` spawns 20 threads with 90% PUTs
- Cache capacity is respected (SIZE never exceeds 3)
- No race conditions during eviction
- All threads complete without deadlock

#### Test 3: Stress test with evictions

```bash
$ echo -e "INIT 2\nCONCURRENT 50 MIXED\nSIZE" | ./your_program.sh
OK
OK      # CONCURRENT spawns 50 threads: 50% reads, 50% writes
2       # SIZE is exactly 2 (many evictions happened safely)
```

**Expected behavior:**
- Small cache (capacity=2) with many threads forces frequent evictions
- Evictions happen correctly under concurrent access
- No corrupted DLL pointers
- No deadlocks or crashes

---

### Notes

<details>
<summary>CONCURRENT command format</summary>

The `CONCURRENT` command spawns multiple threads:

```
CONCURRENT <num_threads> <workload_pattern>

Examples:
CONCURRENT 10 READ_HEAVY   # 10 threads, 70% reads, 30% writes
CONCURRENT 20 WRITE_HEAVY  # 20 threads, 90% writes, 10% reads
CONCURRENT 50 MIXED        # 50 threads, 50% reads, 50% writes
```

Each thread runs for approximately 1 second, performing random operations on random keys (`key_0` to `key_99`).

The tester verifies:
1. No crashes or deadlocks
2. Consistent state after concurrent operations
3. Correct SIZE (no lost updates or double-counting)

</details>

<details>
<summary>Python implementation with threading.Lock</summary>

```python
import threading

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.lock = threading.Lock()  # Add lock
        # ... rest of initialization
    
    def get(self, key: str) -> str | None:
        with self.lock:  # Acquire lock
            # ... existing get logic
            return result
        # Lock automatically released
    
    def put(self, key: str, value: str) -> None:
        with self.lock:  # Acquire lock
            # ... existing put logic
            # ... including eviction if needed
        # Lock automatically released
    
    def size(self) -> int:
        with self.lock:
            return len(self.cache)
```

**Key points:**
- `threading.Lock()` is a simple exclusive lock (one thread at a time)
- `with self.lock:` automatically acquires and releases
- All cache operations (including DLL updates) are protected

**Note:** Python's `threading.Lock` is an exclusive lock, not a read-write lock. For this stage, it's sufficient because:
- The test workload is not heavily read-dominated
- Python's GIL limits true parallelism anyway
- Simpler implementation (no separate read/write lock APIs)

For production Python, consider `threading.RLock` (reentrant lock) if you have nested lock acquisitions.

</details>

<details>
<summary>Java implementation with ReentrantReadWriteLock</summary>

```java
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.concurrent.locks.Lock;

class LRUCache {
    private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();
    private final Lock readLock = rwLock.readLock();
    private final Lock writeLock = rwLock.writeLock();
    
    public String get(String key) {
        readLock.lock();  // Multiple readers OK
        try {
            // ... existing get logic
            return result;
        } finally {
            readLock.unlock();  // Always unlock in finally
        }
    }
    
    public void put(String key, String value) {
        writeLock.lock();  // Exclusive write
        try {
            // ... existing put logic
            // ... including eviction
        } finally {
            writeLock.unlock();
        }
    }
    
    public int size() {
        readLock.lock();
        try {
            return cache.size();
        } finally {
            readLock.unlock();
        }
    }
}
```

**Key points:**
- `ReentrantReadWriteLock` supports multiple concurrent readers
- `readLock()` for GET and SIZE (non-modifying operations)
- `writeLock()` for PUT (modifying operations)
- Always unlock in `finally` block (even if exception thrown)

**Why read-write lock?**
- Better performance for read-heavy workloads
- Multiple GET operations can run simultaneously
- Only PUT operations block (exclusive access)

</details>

<details>
<summary>Go implementation with sync.RWMutex</summary>

```go
import "sync"

type LRUCache struct {
    capacity int
    cache    map[string]*Node
    mu       sync.RWMutex  // Read-Write mutex
    // ... other fields
}

func (c *LRUCache) Get(key string) (string, bool) {
    c.mu.RLock()  // Read lock (multiple readers OK)
    defer c.mu.RUnlock()
    
    // ... existing get logic
    return value, found
}

func (c *LRUCache) Put(key string, value string) {
    c.mu.Lock()  // Write lock (exclusive)
    defer c.mu.Unlock()
    
    // ... existing put logic
    // ... including eviction
}

func (c *LRUCache) Size() int {
    c.mu.RLock()  // Read lock
    defer c.mu.RUnlock()
    
    return len(c.cache)
}
```

**Key points:**
- `sync.RWMutex` is Go's read-write mutex
- `RLock()` for reads, `Lock()` for writes
- `defer` ensures unlock even if panic occurs
- Multiple goroutines can hold read locks simultaneously

</details>

<details>
<summary>Common pitfalls</summary>

**1. Forgetting to lock all operations**
```python
# ❌ WRONG - SIZE is not protected
def size(self):
    return len(self.cache)  # Race condition!

# ✅ CORRECT
def size(self):
    with self.lock:
        return len(self.cache)
```

**2. Deadlock from nested locks**
```python
# ❌ WRONG - can deadlock with non-reentrant lock
def get(self, key):
    with self.lock:
        value = self.cache.get(key)
        if value is not None:
            self._move_to_head(key)  # Tries to acquire lock again!
        return value

# ✅ CORRECT - don't call other locked methods
def get(self, key):
    with self.lock:
        # Inline the logic, don't call _move_to_head
        if key in self.cache:
            node = self.cache[key]
            self._remove_node(node)  # These should NOT acquire lock
            self._add_to_head(node)
            return node.value
        return None
```

**3. Not unlocking in Java (missing finally)**
```java
// ❌ WRONG - lock not released if exception thrown
public void put(String key, String value) {
    writeLock.lock();
    // ... logic that might throw exception
    writeLock.unlock();  // Never reached if exception!
}

// ✅ CORRECT - always unlock in finally
public void put(String key, String value) {
    writeLock.lock();
    try {
        // ... logic
    } finally {
        writeLock.unlock();  // Always executed
    }
}
```

**4. Using wrong lock type for operation**
```java
// ❌ WRONG - GET uses write lock (unnecessary blocking)
public String get(String key) {
    writeLock.lock();  // Blocks all other operations!
    try {
        return cache.get(key);
    } finally {
        writeLock.unlock();
    }
}

// ✅ CORRECT - GET uses read lock (allows concurrent reads)
public String get(String key) {
    readLock.lock();
    try {
        return cache.get(key);
    } finally {
        readLock.unlock();
    }
}
```

**5. Protecting only some operations**
```python
# ❌ WRONG - eviction is not atomic
def put(self, key, value):
    with self.lock:
        self.cache[key] = value
    # Lock released here!
    if len(self.cache) > self.capacity:
        self._evict()  # Race condition: another thread could modify cache!

# ✅ CORRECT - entire operation is atomic
def put(self, key, value):
    with self.lock:
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self._evict()  # Still under lock protection
```

</details>

<details>
<summary>Testing thread safety locally</summary>

You can test thread safety manually before submitting:

**Python:**
```python
import threading
import random

cache = LRUCache(10)

def worker():
    for _ in range(1000):
        op = random.choice(['get', 'put'])
        key = f"key_{random.randint(0, 20)}"
        if op == 'get':
            cache.get(key)
        else:
            cache.put(key, str(random.randint(0, 100)))

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Final size: {cache.size()}")  # Should be <= 10
```

**Java:**
```java
ExecutorService executor = Executors.newFixedThreadPool(10);
for (int i = 0; i < 10; i++) {
    executor.submit(() -> {
        Random rand = new Random();
        for (int j = 0; j < 1000; j++) {
            String key = "key_" + rand.nextInt(20);
            if (rand.nextBoolean()) {
                cache.get(key);
            } else {
                cache.put(key, String.valueOf(rand.nextInt(100)));
            }
        }
    });
}
executor.shutdown();
executor.awaitTermination(10, TimeUnit.SECONDS);
System.out.println("Final size: " + cache.size());  // Should be <= 10
```

**Go:**
```go
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        for j := 0; j < 1000; j++ {
            key := fmt.Sprintf("key_%d", rand.Intn(20))
            if rand.Intn(2) == 0 {
                cache.Get(key)
            } else {
                cache.Put(key, fmt.Sprintf("%d", rand.Intn(100)))
            }
        }
    }()
}
wg.Wait()
fmt.Printf("Final size: %d\n", cache.Size())  // Should be <= 10
```

If you see crashes, panics, or SIZE > capacity, you have a race condition.

</details>

<details>
<summary>Performance considerations</summary>

**Lock granularity:**
- Coarse-grained: One lock for entire cache (simple, but lower throughput)
- Fine-grained: One lock per bucket/node (complex, but higher throughput)
- This stage uses coarse-grained (sufficient for most use cases)

**Read-Write lock benefits:**
```
Workload: 90% reads, 10% writes

Exclusive lock (threading.Lock):
- All operations block each other
- Throughput: ~100 ops/sec

Read-Write lock (RWMutex):
- Multiple reads can run concurrently
- Throughput: ~900 ops/sec (9x improvement!)
```

**When exclusive lock is OK:**
- Python (GIL limits true parallelism anyway)
- Write-heavy workloads (>50% writes)
- Simplicity is more important than performance

**When read-write lock is better:**
- Read-heavy workloads (<20% writes)
- Go/Java (true parallelism)
- Production systems with high throughput

</details>

---

### Resources

- [Python threading.Lock](https://docs.python.org/3/library/threading.html#lock-objects) - Official documentation
- [Java ReentrantReadWriteLock](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/locks/ReentrantReadWriteLock.html) - Official documentation
- [Go sync.RWMutex](https://pkg.go.dev/sync#RWMutex) - Official documentation
- [Race conditions (Wikipedia)](https://en.wikipedia.org/wiki/Race_condition) - Understanding concurrency issues
- [Reader-writer lock (Wikipedia)](https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock) - Theory behind RWMutex
