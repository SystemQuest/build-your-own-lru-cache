The entry point for your LRU Cache implementation is in `app/main.py`.

Study and uncomment the relevant code:

```python
self.capacity = capacity
self.cache = {}
```

```python
return self.cache.get(key)
```

```python
self.cache[key] = value
```

```python
return len(self.cache)
```

Push your changes to pass the first stage:

```
git add .
git commit -m "pass 1st stage" # any msg
git push origin master
```
