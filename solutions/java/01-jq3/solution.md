The entry point for your LRU Cache implementation is in `src/main/java/Main.java`.

Here's the code for the first stage:

```java
File: src/main/java/Main.java

this.capacity = capacity;
this.cache = new HashMap<>();
```

```java
File: src/main/java/Main.java

return cache.get(key);
```

```java
File: src/main/java/Main.java

cache.put(key, value);
```

```java
File: src/main/java/Main.java

return cache.size();
```

Push your changes to pass the first stage:

```
git add .
git commit -m "pass 1st stage" # any msg
git push origin master
```
