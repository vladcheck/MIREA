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
    while (true)
    {
        bool switchHappened = false;
        for (int i = 1; i < arr.size(); i++)
        {
            if (arr[i - 1] > arr[i])
            {
                switchHappened = true;
                swap(arr[i - 1], arr[i]);
            }
        }
        if (!switchHappened)
            break;
    }
    print_each_element(arr);
    return 0;
}