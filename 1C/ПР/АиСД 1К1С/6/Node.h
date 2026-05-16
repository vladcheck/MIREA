#pragma once

struct Node
{
    int value;
    Node *previous = nullptr;
    Node *next = nullptr;
};

void print_node(Node *node)
{
    if (!node)
    {
        std::cout << "Nan Nan Nan" << std::endl;
    }
    else
    {
        std::cout << node->previous->value << " " << node->value << " " << node->next->value << std::endl;
    }
}

void print_node_addresses(Node *node)
{
    if (!node)
    {
        std::cout << "nullptr nullptr nullptr" << std::endl;
    }
    else
    {
        std::cout << node->previous << " " << node << " " << node->next << std::endl;
    }
}