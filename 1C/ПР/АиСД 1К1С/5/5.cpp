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
    const vector<int> shell_sort_gaps = {10, 5, 2, 1};
    vector<int> arr = {20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0};
    print_each_element(arr);
    cout << "\n\n";
    for (auto gap : shell_sort_gaps)
    {
        for (int i = 0; i < arr.size(); i += gap)
        {
            int min_elem = arr[i];
            int min_elem_index = i;
            for (int j = i + gap; j < arr.size(); j += gap)
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
        cout << endl;
    }
    cout << "\n\n";
    print_each_element(arr);
    return 0;
}