#include <string>
#include <iostream>

void newline() {
    std::cout << std::endl;
}

template<typename T, typename U>
struct Entry {
    T key = "";
    U value = "";
    Entry(T k, U v) : key(k), value(v) {}
};

template<typename T, typename U>
struct Node {
    Entry<T, U> value;
    Node<T, U> *next = nullptr;
};

template<typename T, typename U>
class LinkedList {
    int count = 0;
    
    public:
    Node<T,U> *head = nullptr;

    LinkedList(Entry<T,U>* value = nullptr) {
        if (value) {
            head = new Node<T,U>{*value};
            count++;
        }
    }

    ~LinkedList() {
        Node<T, U>* current = head;
        while (current) {
            Node<T,U>* next = current->next;
            delete current;
            current = next;
        }
    }

    void append(Entry<T,U> value) {
        auto* node = new Node<T,U>{value};
        if (!head) {
            head = node;
        } else {
            auto* current = head;
            while (current->next) {
                current = current->next;
            }
            current->next = node;
        }
        count++;
    }

    void print() {
        if (!head) return;
        auto* current = head;
        std::cout << "'" << current->value.key << "': ";
        while (current) {
            std::cout << "'" << current->value.value << "'";
            if (current->next) std::cout << ", ";
            current = current->next;
        }
        newline();
    }

    bool has(Entry<T,U> &entry) {
        auto* current = head;
        while (current) {
            if (current->value.key == entry.key && current->value.value == entry.value) {
                return true;
            }
            current = current->next;
        }
        return false;
    }

    void remove(Node<T,U> *node) {
        if (node == head) {
            head = node->next;
            delete node;
            count--;
            return;
        }
        auto previous = head;
        auto current = head->next;
        auto next = (current) ? current->next : nullptr;

        while (current) {
            if (current == node) {
                previous->next = next;
                delete node;
                count--;
                return;
            }
            previous = current;
            current = current->next;
            next = (current) ? current->next : nullptr;
        }
    }

    bool empty() {
        return count == 0;
    }
};
