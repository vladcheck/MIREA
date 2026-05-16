#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

void print_each_element(vector<int> arr)
{
    for (auto n : arr)
    {
        cout << n << " ";
    }
}

int main()
{
    vector<int> arr = {10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0};
    print_each_element(arr);
    cout << "\n\n";
    for (int i = 0; i < arr.size(); i++)
    {
        int min_elem = arr[i];
        int min_elem_index = i;
        for (int j = i + 1; j < arr.size(); j++)
        {
            if (arr[j] < min_elem)
            {
                min_elem = arr[j];
                min_elem_index = j;
            }
        }
        swap(arr[i], arr[min_elem_index]);
    }
    print_each_element(arr);
    return 0;
}