#include <algorithm>
#include <vector>
#include "linked_list_utilities.h"
#include "linked_list.h"
#include "Node.h"

int main()
{
    LinkedList *list1 = new LinkedList(new int(10), new int(20));
    append(list1, 30);

    LinkedList *list2 = new LinkedList(new int(10), new int(20));
    append(list2, 30);

    std::cout << "Test are_equal: " << std::endl;
    print_list(list1);
    print_list(list2);
    std::cout << are_equal(list1, list2) << std::endl;

    std::cout << "Test includes: " << std::endl;
    append(list1, 40);
    print_list(list1);
    print_list(list2);
    std::cout << are_equal(list1, list2) << std::endl;

    std::cout << "Test has_duplicates: " << std::endl;
    append(list1, 40);
    print_list(list1);
    std::cout << has_duplicates(list1) << std::endl;

    std::cout << "Test move_first_to_last: " << std::endl;
    append(list1, -3);
    print_list(list1);
    move_first_to_last(list1);
    print_list(list1);

    std::cout << "Test move_last_to_first: " << std::endl;
    move_last_to_first(list1);
    print_list(list1);

    std::cout << "Test append_list: " << std::endl;
    LinkedList *list3 = new LinkedList(new int(-1));
    append(list3, -2);
    append(list3, -3);

    print_list(list3);
    print_list(list1);

    append_list(list1, list3);

    print_list(list3);

    std::cout << "Test reverse: " << std::endl;
    append(list2, 100);
    append(list2, 110);
    append(list2, 120);
    append(list2, 130);
    print_list(list2);
    reverse(list2);
    print_list(list2);

    std::cout << "Test leave_unique: " << std::endl;
    append(list1, 10);
    print_list(list1);
    leave_unique(list1);
    print_list(list1);

    delete list1;
    delete list2;
    delete list3;

    return 0;
}