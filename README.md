# Build your own LRU Cache

[![Course](https://img.shields.io/badge/SystemQuest-Course-blue)](https://systemquest.io)
[![Language](https://img.shields.io/badge/Language-Python-green)](https://www.python.org/)

This is a [SystemQuest](https://systemquest.io) course repository for building your own LRU (Least Recently Used) Cache from scratch.

## 📚 Course Overview

In this course, you'll build a fully functional LRU Cache implementation, learning fundamental data structures and caching strategies along the way.

### Stages

1. **Stage 1 - Basic Implementation** 
   - Implement basic cache operations (get, put)
   - Learn dictionary-based storage

2. **Stage 2 - FIFO Cache**
   - Implement First-In-First-Out eviction policy
   - Understand queue-based eviction

3. **Stage 3 - LRU Cache**
   - Implement Least Recently Used eviction policy
   - Use OrderedDict or doubly-linked list + hashmap

4. **Stage 4 - Optimization**
   - Optimize time complexity to O(1) for all operations
   - Implement custom doubly-linked list

5. **Stage 5 - Thread Safety**
   - Add thread-safe operations using locks
   - Handle concurrent access scenarios

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- pipenv

### Running the Course

```bash
# Clone the starter code (will be provided by SystemQuest platform)
git clone <your-starter-repo-url>
cd <your-starter-repo>

# Install dependencies
pipenv install

# Run your implementation
pipenv run python app/main.py
```

## 📖 Course Structure

```
build-your-own-lru-cache/
├── course-definition.yml          # Course metadata and stage definitions
├── compiled_starters/             # Compiled starter code for each language
│   └── python/
├── solutions/                     # Reference solutions for each stage
│   └── python/
│       ├── 01-s1-basic/
│       ├── 02-s2-fifo/
│       ├── 03-s3-lru/
│       ├── 04-s4-optimize/
│       └── 05-s5-thread-safe/
├── starter_templates/             # Templates used to generate starters
│   ├── all/                       # Shared across all languages
│   └── python/                    # Python-specific templates
└── dockerfiles/                   # Docker images for testing
```

## 🛠️ Development

This repository uses the [course-sdk](https://github.com/SystemQuest/course-sdk-go) for course compilation.

### Compile the course

```bash
# Compile Python starters and solutions
course-sdk compile python

# Compile all languages
course-sdk compile
```

## 📝 License

This course content is part of the SystemQuest platform.

## 🤝 Contributing

Course improvements and bug fixes are welcome! Please open an issue or submit a pull request.

## 📧 Contact

- Website: [https://systemquest.io](https://systemquest.dev)
- GitHub: [@SystemQuest](https://github.com/SystemQuest)

---

**Happy Coding!** 🎉
