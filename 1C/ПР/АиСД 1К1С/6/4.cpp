#include <iostream>
#include <cstdlib>
#include "Node.h"
#include "linked_list.h"

int main()
{
    std::srand(time(0));
    LinkedList *l = new LinkedList();
    populate_linked_list(l, 20);

    int sum = 0;
    Node *current = l->head;
    while (current != nullptr)
    {
        sum += current->value;
        std::cout << current->value << " ";
        current = current->next;
    }
    std::cout << std::endl;
    std::cout << sum;
    return 0;
}