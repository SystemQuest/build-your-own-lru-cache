# Build your own LRU Cache

[![Course](https://img.shields.io/badge/SystemQuest-Course-blue)](https://systemquest.io)
[![Languages](https://img.shields.io/badge/Languages-Python%20%7C%20Go%20%7C%20Java-green)]()

This is a [SystemQuest](https://systemquest.io) course repository for building your own LRU (Least Recently Used) Cache from scratch in Python, Go, or Java.

## 📚 Course Overview

In this course, you'll build a fully functional LRU Cache implementation, learning fundamental data structures and caching strategies along the way.

### Stages

1. **Stage 1 (jq3) - Basic Cache Operations** 
   - Implement basic cache operations (INIT, GET, PUT, SIZE)
   - Learn dictionary-based storage
   - Handle stdin/stdout communication

2. **Stage 2 (ze6) - FIFO Eviction**
   - Implement First-In-First-Out eviction policy
   - Understand capacity enforcement
   - Learn insertion order tracking

3. **Stage 3 (ch7) - LRU with Built-in Data Structures** ⭐ Quick Win
   - Implement Least Recently Used eviction policy
   - Use language built-ins for fast implementation (OrderedDict/LinkedHashMap/List+Map)
   - Understand access order vs insertion order

4. **Stage 4 (vh5) - Custom Doubly Linked List** ⭐⭐ Core Value
   - Build LRU from scratch (no OrderedDict!)
   - Implement HashMap + Doubly Linked List pattern
   - Master the LeetCode #146 solution
   - Prove O(1) complexity for all operations

5. **Stage 5 (ba6) - Production Grade** ⭐ Real World
   - Add thread-safe operations with locks
   - Implement statistics and monitoring
   - Support TTL (Time-To-Live) expiration
   - Build production-ready cache

## 🚀 Getting Started

### Prerequisites

Choose your language:

- **Python**: Python 3.13+ and pipenv
- **Go**: Go 1.21+ 
- **Java**: Java 17+ and Maven/Gradle

### Running the Course

**Python:**
```bash
git clone <your-starter-repo-url>
cd <your-starter-repo>
pipenv install
pipenv run python app/main.py
```

**Go:**
```bash
git clone <your-starter-repo-url>
cd <your-starter-repo>
go mod download
go run ./cmd/main.go
```

**Java:**
```bash
git clone <your-starter-repo-url>
cd <your-starter-repo>
mvn compile
mvn exec:java -Dexec.mainClass="com.systemquest.lrucache.Main"
```

## 📖 Course Structure

```
build-your-own-lru-cache/
├── course-definition.yml          # Course metadata and stage definitions
├── compiled_starters/             # Compiled starter code for each language
│   ├── python/
│   ├── go/
│   └── java/
├── solutions/                     # Reference solutions for each stage
│   ├── python/
│   ├── go/
│   └── java/
├── starter_templates/             # Templates used to generate starters
│   ├── all/                       # Shared across all languages
│   ├── python/                    # Python-specific templates
│   ├── go/                        # Go-specific templates
│   └── java/                      # Java-specific templates
└── dockerfiles/                   # Docker images for testing
    ├── python.Dockerfile
    ├── go.Dockerfile
    └── java.Dockerfile
```

## 🛠️ Development

This repository uses the [course-sdk](https://github.com/SystemQuest/course-sdk-go) for course compilation.

### Compile the course

```bash
# Compile specific language
course-sdk compile python
course-sdk compile go
course-sdk compile java

# Compile all languages
course-sdk compile
```

## 📝 License

This course content is part of the SystemQuest platform.

## 🤝 Contributing

Course improvements and bug fixes are welcome! Please open an issue or submit a pull request.

## 📧 Contact

- Website: [https://systemquest.dev](https://systemquest.dev)
- GitHub: [@SystemQuest](https://github.com/SystemQuest)

---

**Happy Coding!** 🎉
