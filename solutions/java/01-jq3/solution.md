The entry point for your LRU Cache implementation is in `src/main/java/Main.java`.

Here's the code for the first stage:

```java
File: src/main/java/Main.java

/**
 * LRU Cache implementation
 */
class LRUCache {
    private final int capacity;
    private final Map<String, String> cache;
    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new HashMap<>();
    }
    public String get(String key) {
        return cache.get(key);
    }
    public void put(String key, String value) {
        cache.put(key, value);
    }
    public int size() {
        return cache.size();
    }
}
```

```java
File: src/main/java/Main.java

LRUCache cache = null;
BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
String line;
while ((line = reader.readLine()) != null) {
    line = line.trim();
    if (line.isEmpty()) {
        continue;
    }
    String[] parts = line.split("\\s+");
    String command = parts[0];
    switch (command) {
        case "INIT":
            int capacity = Integer.parseInt(parts[1]);
            cache = new LRUCache(capacity);
            System.out.println("OK");
            break;
        case "PUT":
            if (cache == null) {
                System.out.println("ERROR: Cache not initialized");
                continue;
            }
            String putKey = parts[1];
            String putValue = parts[2];
            cache.put(putKey, putValue);
            System.out.println("OK");
            break;
        case "GET":
            if (cache == null) {
                System.out.println("ERROR: Cache not initialized");
                continue;
            }
            String getKey = parts[1];
            String result = cache.get(getKey);
            if (result == null) {
                System.out.println("NULL");
            } else {
                System.out.println(result);
            }
            break;
        case "SIZE":
            if (cache == null) {
                System.out.println("ERROR: Cache not initialized");
                continue;
            }
            System.out.println(cache.size());
            break;
        default:
            System.out.println("ERROR: Unknown command: " + command);
            break;
    }
}
```

Push your changes to pass the first stage:

```
git add .
git commit -m "pass 1st stage" # any msg
git push origin master
```
