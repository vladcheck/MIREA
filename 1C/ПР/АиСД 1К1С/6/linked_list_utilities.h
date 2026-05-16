#pragma once
#include <vector>
#include <algorithm>
#include <iostream>
#include "Node.h"
#include "linked_list.h"

bool is_empty(LinkedList *l)
{
    return l->head == nullptr;
}

int size(LinkedList *l)
{
    if (l->head == nullptr)
        return 0;
    int res = 1;
    Node *current = l->head;
    while (current->next != nullptr)
    {
        res++;
        current = current->next;
    }
    return res;
}

void set_first_node(LinkedList *l, Node *node)
{
    l->head = node;
    l->tail = node;
}

void append(LinkedList *l, int value)
{
    Node *new_node = new Node{value};
    if (size(l) == 0)
    {
        set_first_node(l, new_node);
    }
    else
    {
        new_node->previous = l->tail;
        l->tail->next = new_node;
        l->tail = new_node;
    }
}

void prepend(LinkedList *l, int value)
{
    Node *new_node = new Node{value};
    if (size(l) == 0)
    {
        set_first_node(l, new_node);
    }
    else
    {
        new_node->next = l->head;
        l->head->previous = new_node;
        l->head = new_node;
    }
}

void insert(LinkedList *l, int index, int value)
{
    if (index < 0 || index > size(l) - 1)
        return;
    else if (index == 0)
    {
        prepend(l, value);
        return;
    }
    else if (index == size(l) - 1)
    {
        append(l, value);
        return;
    }
    Node *new_node = new Node{value, nullptr};
    Node *current = l->head;
    Node *before_current = current->previous;

    for (int i = 0; i < index; i++)
    {
        before_current = current;
        current = current->next;
    }
    new_node->next = current;
    before_current->next = new_node;
}

LinkedList *cutout_list(LinkedList *l)
{
    if (size(l) == 0)
    {
        return new LinkedList();
    }
    else if (size(l) == 1)
    {
        return new LinkedList(&l->head->value);
    }
    else
    {
        LinkedList *new_list = new LinkedList();
        Node *current = l->head->next;
        while (current)
        {
            append(new_list, current->value);
            current = current->next;
        }
        return new_list;
    }
}

bool are_equal(LinkedList *l1, LinkedList *l2)
{
    if (size(l1) != size(l2))
        return false;
    Node *current1 = l1->head;
    Node *current2 = l2->head;
    while (current1 && current2)
    {
        if (current1->value != current2->value)
        {
            return false;
        }
        else
        {
            current1 = current1->next;
            current2 = current2->next;
        }
    }
    return true;
}

bool includes(LinkedList *inner, LinkedList *outer)
{
    // пустой список не содержит в себе непустой
    if (size(inner) == 0 && size(outer) != 0)
        return false;
    // список всегда содержит в себе список из нуля нодов
    else if (size(outer) == 0)
        return true;
    std::vector<int> inner_values;
    Node *inner_current = inner->head;

    while (inner_current)
    {
        inner_values.push_back(inner_current->value);
        inner_current = inner_current->next;
    }

    Node *outer_current = outer->head;

    while (outer_current)
    {
        if (std::find(inner_values.begin(), inner_values.end(), outer_current->value) == inner_values.end())
        {
            return false;
        }
        outer_current = outer_current->next;
    }
    return true;
}

bool has_duplicates(LinkedList *l)
{
    std::vector<int> met;
    Node *current = l->head;
    while (current)
    {
        for (int n : met)
        {
            if (n == current->value)
                return true;
        }
        met.push_back(current->value);
        current = current->next;
    }
    return false;
}

void move_first_to_last(LinkedList *l)
{
    if (size(l) <= 1)
        return;
    Node *first = l->head;
    l->head = first->next;
    l->head->previous = nullptr;
    first->next = nullptr;
    first->previous = l->tail;
    l->tail->next = first;
    l->tail = first;
}

void move_last_to_first(LinkedList *l)
{
    if (size(l) <= 1)
        return;
    Node *before_tail = l->tail->previous;
    Node *tail = l->tail;
    l->tail = before_tail;
    before_tail->next = nullptr;
    tail->next = l->head;
    l->head->previous = tail;
    l->head = tail;
}

void append_list(LinkedList *from, LinkedList *to)
{
    Node *current = from->head;
    while (current)
    {
        append(to, current->value);
        current = current->next;
    }
}

void reverse(LinkedList *l)
{
    std::vector<Node *> nodes;
    Node *current = l->head;

    while (current)
    {
        nodes.push_back(current);
        current = current->next;
    }
    for (Node *node : nodes)
    {
        node->previous = nullptr;
        node->next = nullptr;
    }

    std::reverse(nodes.begin(), nodes.end());

    for (int i = 0; i < nodes.size(); i++)
    {
        if (i - 1 >= 0)
        {
            nodes[i - 1]->next = nodes[i];
            nodes[i]->previous = nodes[i - 1];
        }
    }

    l->head = nodes[0];
    l->tail = nodes[nodes.size() - 1];
}

void remove_node_by_two_pointers(LinkedList *l, Node *before, Node *to_remove, Node *to_attach_to)
{
    if (to_attach_to)
    {
        before->next = to_attach_to;
        to_attach_to->previous = before;
    }
    else
    {
        Node *before_tail = before->previous;
        l->tail = before;
        l->tail->previous = before_tail;
        l->tail->next = nullptr;
    }
    delete to_remove;
}

void leave_unique(LinkedList *l)
{
    if (size(l) <= 1)
        return;
    std::vector<int> unqiue_values = {l->head->value};
    Node *previous = l->head;
    Node *current = previous->next;
    Node *next = (current) ? current->next : nullptr;
    while (current)
    {
        if (std::find(unqiue_values.begin(), unqiue_values.end(), current->value) != unqiue_values.end())
        {
            remove_node_by_two_pointers(l, previous, current, next);
            // previous остается на своем месте, так как нод по адресу current был уничтожен
        }
        else
        {
            unqiue_values.push_back(current->value);
            previous = current;
        }
        current = next;
        next = (next) ? next->next : nullptr;
    }
}