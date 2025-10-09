The entry point for your LRU Cache implementation is in `app/main.go`.

Study and uncomment the relevant code:

```go

type LRUCache struct {
	capacity int
	cache    map[string]string
}

func NewLRUCache(capacity int) *LRUCache {
	return &LRUCache{
		capacity: capacity,
		cache:    make(map[string]string),
	}
}

func (c *LRUCache) Get(key string) (string, bool) {
	value, ok := c.cache[key]
	return value, ok
}

func (c *LRUCache) Put(key, value string) {
	c.cache[key] = value
}

func (c *LRUCache) Size() int {
	return len(c.cache)
}
```

```go

var cache *LRUCache
scanner := bufio.NewScanner(os.Stdin)

for scanner.Scan() {
	line := strings.TrimSpace(scanner.Text())
	if line == "" {
		continue
	}

	parts := strings.Fields(line)
	command := parts[0]

	switch command {
	case "INIT":
		if len(parts) < 2 {
			fmt.Println("ERROR: INIT requires capacity argument")
			continue
		}
		capacity, err := strconv.Atoi(parts[1])
		if err != nil {
			fmt.Printf("ERROR: Invalid capacity: %v\n", err)
			continue
		}
		cache = NewLRUCache(capacity)
		fmt.Println("OK")

	case "PUT":
		if cache == nil {
			fmt.Println("ERROR: Cache not initialized")
			continue
		}
		if len(parts) < 3 {
			fmt.Println("ERROR: PUT requires key and value arguments")
			continue
		}
		key := parts[1]
		value := parts[2]
		cache.Put(key, value)
		fmt.Println("OK")

	case "GET":
		if cache == nil {
			fmt.Println("ERROR: Cache not initialized")
			continue
		}
		if len(parts) < 2 {
			fmt.Println("ERROR: GET requires key argument")
			continue
		}
		key := parts[1]
		value, ok := cache.Get(key)
		if !ok {
			fmt.Println("NULL")
		} else {
			fmt.Println(value)
		}

	case "SIZE":
		if cache == nil {
			fmt.Println("ERROR: Cache not initialized")
			continue
		}
		fmt.Println(cache.Size())

	default:
		fmt.Printf("ERROR: Unknown command: %s\n", command)
	}
}

if err := scanner.Err(); err != nil {
	fmt.Fprintf(os.Stderr, "Error reading input: %v\n", err)
	os.Exit(1)
}
```

Push your changes to pass the first stage:

```
git add .
git commit -m "pass 1st stage" # any msg
git push origin master
```
