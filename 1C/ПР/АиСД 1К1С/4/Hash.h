#pragma once
#include "LinkedList.h"
#include <vector>
#include <cmath>
#include <string>

const int M = 1e9 + 9;

template<typename T, typename U>
class HashTable {
    std::vector<LinkedList<T,U>> table;

    int polynomial_rolling_hash(std::string& key) {
        long long H = 0;
        long long p = 1;
        for (int i = 0; i < key.size(); i++) {
            H = (H + key[i] * p) % M;
            p = (p * 31) % M;
        }
        return H;
    }

    int polynomial_rolling_hash(int key) {
        return key % table.size();
    }

    int hash_function(T& key) {
        return polynomial_rolling_hash(key) % table.size();
    }

    public:
    HashTable(int capacity = 100) : table(capacity) {}

    void add(Entry<T,U> entry) {
        int key = hash_function(entry.key);
        if (!table[key].has(entry)) {
            table[key].append(entry);
        }
    }

    std::vector<U> retrieve(char key) {
        const int hash_key = hash_function(key);
        std::vector<U> values{};
        auto current = table[hash_key].head;
        
        while (current) {
            if (current->value.key == key){
                values.push_back(current->value.value);
            }
            current = current->next;
        }
        return values;
    }

    std::vector<U> retrieve(std::string key) {
        const int hash_key = hash_function(key);
        std::vector<U> values{};
        auto current = table[hash_key].head;
        
        while (current) {
            if (current->value.key.compare(key) == 0){
                values.push_back(current->value.value);
            }
            current = current->next;
        }
        return values;
    }

    void remove(Entry<T,U> entry) {
        const int hash_key = hash_function(entry.key);
        if (!table[hash_key].has(entry)) return;

        auto current = table[hash_key].head;
        while (current) {
            if (current->value.key == entry.key && current->value.value == entry.value) {
                table[hash_key].remove(current);
                break;
            }
            current = current->next;
        }
    }

    bool has_key(T key) {
        return this->retrieve(key).size() > 0;
    }

    void print() {
        if (table.size() == 0) return;
        for (auto& list : table) {
            list.print();
        }
        newline();
    }
};
