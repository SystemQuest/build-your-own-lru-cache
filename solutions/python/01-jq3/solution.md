The entry point for your LRU Cache implementation is in `app/main.py`.

Here's the code for the first stage:

```python
File: app/main.py

self.capacity = capacity
self.cache = {}
```

```python
File: app/main.py

return self.cache.get(key)
```

```python
File: app/main.py

self.cache[key] = value
```

```python
File: app/main.py

return len(self.cache)
```

Push your changes to pass the first stage:

```
git add .
git commit -m "pass 1st stage" # any msg
git push origin master
```
