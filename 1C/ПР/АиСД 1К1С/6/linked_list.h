#pragma once
#include <iostream>
#include "Node.h"

class LinkedList
{
public:
    Node *head = nullptr;
    Node *tail = nullptr;

    LinkedList(int *value_for_head = nullptr, int *value_for_tail = nullptr)
    {
        if (value_for_head)
        {
            this->head = new Node{*value_for_head};
            if (value_for_tail)
            {
                this->tail = new Node{*value_for_tail};
                this->tail->previous = this->head;
                this->head->next = this->tail;
            }
            else
            {
                this->tail = this->head;
            }
        }
    }
};

void populate_linked_list(LinkedList *l, int n)
{
    Node *curr = l->head;
    Node *last = l->head;

    for (int i = 0; i < n; i++)
    {
        const int val = std::rand() % 100 + 1;
        Node *node = new Node{val, nullptr};
        curr->next = node;
        curr = curr->next;
        last = curr->next;
    }
    l->tail = last;
}

void print_list(LinkedList *l)
{
    Node *current = l->head;
    while (current)
    {
        std::cout << current->value << " -> ";
        current = current->next;
    }
    std::cout << "nullptr | head: " << l->head->value << "; tail: " << l->tail->value << "\n";
}