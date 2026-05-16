#include <iostream>
#include "Node.h"
#include "linked_list.h"
#include "linked_list_utilities.h"

int main()
{
    LinkedList *list = new LinkedList();

    std::cout << "Testing prepend:" << std::endl;
    prepend(list, 10);
    print_list(list);

    prepend(list, 20);
    print_list(list);

    std::cout << "Testing append:" << std::endl;
    append(list, 30);
    print_list(list);

    append(list, 40);
    print_list(list);

    std::cout << "Testing insert:" << std::endl;
    insert(list, 2, 25);
    print_list(list);

    insert(list, 0, 5); // в начало
    print_list(list);

    insert(list, 5, 35); // в конец
    print_list(list);

    std::cout << "Size of the list: " << size(list) << std::endl;

    std::cout << "Testing cutout_list:" << std::endl;
    LinkedList *cut_list = cutout_list(list);
    print_list(cut_list);

    delete list;
    delete cut_list;

    return 0;
}