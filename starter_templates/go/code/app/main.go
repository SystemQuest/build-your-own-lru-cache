package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

// Prevents unused imports from being removed by goimports
var _ = bufio.NewScanner
var _ = strconv.Atoi
var _ = strings.Fields
var _ = strconv.Atoi

// Uncomment this to pass the first stage
//
// type LRUCache struct {
// 	capacity int
// 	cache    map[string]string
// }
//
// func NewLRUCache(capacity int) *LRUCache {
// 	return &LRUCache{
// 		capacity: capacity,
// 		cache:    make(map[string]string),
// 	}
// }
//
// func (c *LRUCache) Get(key string) (string, bool) {
// 	value, ok := c.cache[key]
// 	return value, ok
// }
//
// func (c *LRUCache) Put(key, value string) {
// 	c.cache[key] = value
// }
//
// func (c *LRUCache) Size() int {
// 	return len(c.cache)
// }

func main() {
	// You can use print statements as follows for debugging, they'll be visible when running tests.
	fmt.Fprintln(os.Stderr, "Logs from your program will appear here!")

	// Uncomment this block to pass the first stage
	//
	// var cache *LRUCache
	// scanner := bufio.NewScanner(os.Stdin)
	//
	// for scanner.Scan() {
	// 	line := strings.TrimSpace(scanner.Text())
	// 	if line == "" {
	// 		continue
	// 	}
	//
	// 	parts := strings.Fields(line)
	// 	command := parts[0]
	//
	// 	switch command {
	// 	case "INIT":
	// 		if len(parts) < 2 {
	// 			fmt.Println("ERROR: INIT requires capacity argument")
	// 			continue
	// 		}
	// 		capacity, err := strconv.Atoi(parts[1])
	// 		if err != nil {
	// 			fmt.Printf("ERROR: Invalid capacity: %v\n", err)
	// 			continue
	// 		}
	// 		cache = NewLRUCache(capacity)
	// 		fmt.Println("OK")
	//
	// 	case "PUT":
	// 		if cache == nil {
	// 			fmt.Println("ERROR: Cache not initialized")
	// 			continue
	// 		}
	// 		if len(parts) < 3 {
	// 			fmt.Println("ERROR: PUT requires key and value arguments")
	// 			continue
	// 		}
	// 		key := parts[1]
	// 		value := parts[2]
	// 		cache.Put(key, value)
	// 		fmt.Println("OK")
	//
	// 	case "GET":
	// 		if cache == nil {
	// 			fmt.Println("ERROR: Cache not initialized")
	// 			continue
	// 		}
	// 		if len(parts) < 2 {
	// 			fmt.Println("ERROR: GET requires key argument")
	// 			continue
	// 		}
	// 		key := parts[1]
	// 		value, ok := cache.Get(key)
	// 		if !ok {
	// 			fmt.Println("NULL")
	// 		} else {
	// 			fmt.Println(value)
	// 		}
	//
	// 	case "SIZE":
	// 		if cache == nil {
	// 			fmt.Println("ERROR: Cache not initialized")
	// 			continue
	// 		}
	// 		fmt.Println(cache.Size())
	//
	// 	default:
	// 		fmt.Printf("ERROR: Unknown command: %s\n", command)
	// 	}
	// }
	//
	// if err := scanner.Err(); err != nil {
	// 	fmt.Fprintf(os.Stderr, "Error reading input: %v\n", err)
	// 	os.Exit(1)
	// }
}
