In this extension stage, you'll add comprehensive metrics and statistics to your LRU cache.

```python
cache.stats()
# Output:
# hits: 850, misses: 150, hit_rate: 85.0%
# evictions: 42, size: 100, capacity: 100
```

Production caches need observability - without metrics, you're flying blind.

### Extension Prerequisites

This is an **optional extension** that adds monitoring capabilities to your cache. You should have completed **Base Stages 1-6** before attempting this extension.

**What you'll have after Base Stages:**
- ✅ O(1) LRU cache with thread safety
- ✅ TTL expiration support
- ✅ Production-ready caching functionality

**What this extension adds:**
- 📊 Hit rate and miss rate tracking
- 📈 Eviction counters and memory insights
- 🔍 Debugging and performance analysis tools
- 🎯 Production observability patterns

---

### Why Cache Statistics Matter

<details>
<summary>Background: Observability in production systems</summary>

Imagine your cache in production. Without metrics, you can't answer:

**Performance questions:**
- "Is my cache helping?" (hit rate = 30% → it's useless!)
- "Why is my API slow?" (high miss rate → cold cache)
- "Did my cache size increase help?" (compare hit rates before/after)

**Capacity planning:**
- "Should I increase cache size?" (evictions/sec too high)
- "How much memory am I using?" (memory_bytes growing)
- "Is TTL too aggressive?" (expiration_count vs eviction_count)

**Real-world example:**
```
Redis cache metrics:
- Hit rate: 99.2% ← GOOD! Cache is effective
- Evictions: 1200/hour ← Consider increasing capacity
- Memory: 2.1 GB / 4 GB ← Room to grow
- TTL expirations: 500/hour ← Working as expected
```

**Common patterns:**

| Hit Rate | Diagnosis | Action |
|----------|-----------|--------|
| **>95%** | Excellent | Cache is working well |
| **80-95%** | Good | Normal for most workloads |
| **50-80%** | Mediocre | Consider larger capacity or better TTL |
| **<50%** | Poor | Cache may not be helping (or cold) |

**Why this matters:**
- **Cost**: Low hit rate wastes memory/CPU
- **Latency**: Misses mean slow database queries
- **Scalability**: Wrong cache size hurts throughput

</details>

---

### Implementation Requirements

To pass this stage, your program will need to:

1. **Track 6 key metrics** (as integers):
   - `hits`: Number of successful GET operations (key found)
   - `misses`: Number of failed GET operations (key not found)
   - `evictions`: Number of entries removed due to capacity
   - `expirations`: Number of entries removed due to TTL expiration
   - `size`: Current number of entries
   - `capacity`: Maximum capacity

2. **Increment counters atomically** (inside locks):
   - `hits++` when GET returns a value (key found and not expired)
   - `misses++` when GET returns NULL (key not found OR expired)
   - `evictions++` when removing LRU item due to capacity
   - `expirations++` when removing item due to TTL expiration
   - Update `size` on PUT/eviction/expiration

3. **Implement STATS command**:
   ```bash
   STATS
   # Output (one line):
   hits:850 misses:150 hit_rate:85.00 evictions:42 expirations:8 size:100 capacity:100
   ```

4. **Calculate hit rate** (percentage with 2 decimal places):
   ```python
   total_requests = hits + misses
   hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0.0
   # Format: "85.00" (not "85.0" or "85")
   ```

**Important:** All operations must remain O(1). Stats command should just read counters (no iteration).

---

### Tests

The tester will verify that your metrics track correctly across different operations.

#### Test 1: Basic hit/miss tracking

```bash
$ echo -e "INIT 5\nPUT a 1\nPUT b 2\nGET a\nGET c\nGET a\nSTATS" | ./your_program.sh
OK
OK
OK
1       # Hit (a exists)
NULL    # Miss (c doesn't exist)
1       # Hit (a exists)
hits:2 misses:1 hit_rate:66.67 evictions:0 expirations:0 size:2 capacity:5
```

**What's being tested:**
- `hits = 2`: GET a (twice) succeeded
- `misses = 1`: GET c failed
- `hit_rate = 66.67`: 2 / (2 + 1) * 100
- `size = 2`: a and b still in cache
- `evictions = 0`: No capacity limit reached

#### Test 2: Eviction tracking

```bash
$ echo -e "INIT 2\nPUT a 1\nPUT b 2\nGET a\nPUT c 3\nGET b\nSTATS" | ./your_program.sh
OK
OK
OK
1       # Hit
OK      # Evicts b (LRU)
NULL    # Miss (b was evicted)
hits:1 misses:1 hit_rate:50.00 evictions:1 expirations:0 size:2 capacity:2
```

**What's being tested:**
- `evictions = 1`: PUT c evicted b (LRU policy)
- `GET b` is a miss (b was evicted)
- `size = 2`: Cache is full (a, c)

#### Test 3: Expiration tracking (TTL)

```bash
$ echo -e "INIT 5\nPUT a 1 1\nPUT b 2\nSLEEP 1.5\nGET a\nGET b\nSTATS" | ./your_program.sh
OK
OK
OK
OK
NULL    # Miss (a expired)
2       # Hit (b still valid)
hits:1 misses:1 hit_rate:50.00 evictions:0 expirations:1 size:1 capacity:5
```

**What's being tested:**
- `expirations = 1`: GET a triggered lazy deletion (TTL expired)
- `evictions = 0`: No capacity-based eviction
- `hits = 1, misses = 1`: GET b succeeded, GET a failed
- `size = 1`: Only b remains

<details>
<summary>All test cases (11 total)</summary>

The tester runs these scenarios:

1. **st8**: Basic hit/miss tracking
2. **st8-empty**: STATS on empty cache (zero division edge case)
3. **st8-hits-only**: All GETs succeed (100% hit rate)
4. **st8-misses-only**: All GETs fail (0% hit rate)
5. **st8-eviction**: Eviction tracking (capacity limit)
6. **st8-eviction-cycle**: Multiple evictions (fill, evict, refill)
7. **st8-expiration**: TTL expiration tracking
8. **st8-mixed**: Mix of TTL expiration and LRU eviction
9. **st8-precision**: Hit rate is exactly 2 decimals (e.g., "66.67", not "66.7")
10. **st8-large**: 100 operations, verify counter accuracy (keys 0-14 pattern)
11. **st8-concurrent**: Thread-safe metrics (10 threads, CONCURRENT command)

</details>

---

### Additional Commands for Testing

#### CONCURRENT Command

For the concurrent test (st8-concurrent), you'll need to implement the `CONCURRENT` command:

```bash
CONCURRENT <num_threads> <workload_pattern>
```

**Parameters:**
- `num_threads`: Number of threads to spawn (e.g., 10)
- `workload_pattern`: One of:
  - `READ_HEAVY`: 70% reads, 30% writes
  - `WRITE_HEAVY`: 10% reads, 90% writes
  - `MIXED`: 50% reads, 50% writes

**Behavior:**
- Spawns N threads that run for ~1 second
- Each thread randomly accesses keys 0-99
- Tests thread-safety of statistics counters
- Returns `OK` when all threads complete

**Example implementation:**

```python
def run_concurrent_workload(cache, workload, duration=1.0):
    """Run random cache operations for 'duration' seconds"""
    end_time = time.time() + duration
    read_prob = {'READ_HEAVY': 0.7, 'WRITE_HEAVY': 0.1, 'MIXED': 0.5}[workload]
    
    while time.time() < end_time:
        key = f"key_{random.randint(0, 99)}"
        if random.random() < read_prob:
            cache.get(key)  # Read
        else:
            cache.put(key, str(random.randint(0, 999)))  # Write

# In main loop:
elif command == "CONCURRENT":
    num_threads = int(parts[1])
    workload = parts[2]
    
    threads = [threading.Thread(target=run_concurrent_workload, args=(cache, workload)) 
               for _ in range(num_threads)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    print("OK")
```

This command is used to verify that your statistics counters are thread-safe (all updates happen inside locks).

---

### Notes

#### Python Implementation

Add 4 metrics fields to `__init__`:

```python
# Add to LRUCache.__init__()
self.hits = 0
self.misses = 0
self.evictions = 0
self.expirations = 0
```

Update `get()` to track hits/misses:

```python
def get(self, key):
    with self.lock:
        if key not in self.cache:
            self.misses += 1  # Key not found
            return None
        
        node = self.cache[key]
        
        # Check expiration
        if node.expire_at and time.time() >= node.expire_at:
            self._remove_node(node)
            del self.cache[key]
            self.expirations += 1
            self.misses += 1  # Expired = miss
            return None
        
        self.hits += 1  # Success
        self._move_to_head(node)
        return node.value
```

Update `put()` to track evictions:

```python
def put(self, key, value, ttl=None):
    with self.lock:
        # ... existing update logic
        
        if key not in self.cache and len(self.cache) >= self.capacity:
            # Evict LRU
            lru_node = self.dll_tail.prev
            self._remove_node(lru_node)
            del self.cache[lru_node.key]
            self.evictions += 1  # Track eviction
        
        # ... rest of put logic
```

Implement `stats()`:

```python
def stats(self):
    with self.lock:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        
        return (
            f"hits:{self.hits} misses:{self.misses} "
            f"hit_rate:{hit_rate:.2f} "
            f"evictions:{self.evictions} expirations:{self.expirations} "
            f"size:{len(self.cache)} capacity:{self.capacity}"
        )
```

Add STATS command to `main.py`:

```python
elif command == "STATS":
    print(cache.stats())
```

<details>
<summary>Java Implementation</summary>

Add metrics fields and track inside locks:

```java
// Add to LRUCache class
private long hits = 0, misses = 0, evictions = 0, expirations = 0;

public String get(String key) {
    lock.readLock().lock();
    try {
        if (!cache.containsKey(key)) {
            misses++;
            return null;
        }
        
        Node node = cache.get(key);
        if (node.expireAt != null && System.currentTimeMillis() >= node.expireAt) {
            // Upgrade to write lock for deletion
            expirations++;
            misses++;
            return null;
        }
        
        hits++;
        moveToHead(node);
        return node.value;
    } finally {
        lock.readLock().unlock();
    }
}

public String stats() {
    long total = hits + misses;
    double hitRate = total > 0 ? (hits / (double) total * 100) : 0.0;
    
    return String.format(
        "hits:%d misses:%d hit_rate:%.2f evictions:%d expirations:%d size:%d capacity:%d",
        hits, misses, hitRate, evictions, expirations, cache.size(), capacity
    );
}
```

</details>

<details>
<summary>Go Implementation</summary>

Use `sync.RWMutex` to protect metrics:

```go
// Add to LRUCache struct
hits, misses, evictions, expirations int64

func (c *LRUCache) Get(key string) (string, bool) {
    c.mu.Lock()
    defer c.mu.Unlock()
    
    node, exists := c.cache[key]
    if !exists {
        c.misses++
        return "", false
    }
    
    if node.expireAt != nil && time.Now().Unix() >= *node.expireAt {
        c.expirations++
        c.misses++
        return "", false
    }
    
    c.hits++
    c.moveToHead(node)
    return node.value, true
}

func (c *LRUCache) Stats() string {
    total := c.hits + c.misses
    var hitRate float64
    if total > 0 {
        hitRate = float64(c.hits) / float64(total) * 100
    }
    
    return fmt.Sprintf(
        "hits:%d misses:%d hit_rate:%.2f evictions:%d expirations:%d size:%d capacity:%d",
        c.hits, c.misses, hitRate, c.evictions, c.expirations, len(c.cache), c.capacity,
    )
}
```

</details>

---

### Common Mistakes

#### 1. **Counting expiration as eviction** ❌

```python
# Wrong: Incrementing evictions when TTL expires
def get(self, key):
    if expired:
        self.evictions += 1  # ❌ Should be self.expirations += 1
```

**Fix:** Use separate counters. Eviction = capacity limit, expiration = TTL.

#### 2. **Forgetting to track misses on expiration** ❌

```python
# Wrong: Only tracking hits, not misses
def get(self, key):
    if expired:
        self.expirations += 1
        # ❌ Missing: self.misses += 1
        return None
```

**Fix:** Expired GET is still a miss from the caller's perspective.

#### 3. **Hit rate with wrong precision** ❌

```python
# Wrong: Inconsistent decimal places
hit_rate = (hits / total * 100)
return f"hit_rate:{hit_rate}"  # Output: "66.7" or "100" (wrong)
```

**Fix:** Always use `.2f` format specifier:
```python
return f"hit_rate:{hit_rate:.2f}"  # Output: "66.67" or "100.00" (correct)
```

#### 4. **Zero division error** ❌

```python
# Wrong: Crash on empty cache
hit_rate = hits / (hits + misses) * 100  # ZeroDivisionError!
```

**Fix:** Handle zero requests:
```python
total = hits + misses
hit_rate = (hits / total * 100) if total > 0 else 0.0
```

---

### Resources

- [Redis INFO command](https://redis.io/commands/info/) - Real-world cache metrics
- [Memcached stats](https://github.com/memcached/memcached/wiki/Commands#statistics) - Industry standard
- [Hit rate calculation](https://en.wikipedia.org/wiki/Cache_performance_measurement_and_metric)

---

**Next Steps:**

After completing this extension, your cache has production-grade observability! You can:

1. **Tune cache size** based on hit rate metrics
2. **Monitor performance** in production
3. **Debug issues** with detailed statistics
4. **Make data-driven decisions** about TTL and capacity

Future extensions you could explore:
- **Persistence**: Save/load cache to disk
- **Distributed**: Multi-node cache with consistent hashing
- **Advanced eviction**: LFU, ARC, custom policies
