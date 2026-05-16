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
    bool switchHappened;
    int l = 1, r = arr.size() - 1;
    do
    {
        switchHappened = false;
        for (int i = l; i < r; i++)
        {
            if (arr[i - 1] > arr[i])
            {
                switchHappened = true;
                swap(arr[i - 1], arr[i]);
            }
        }
        for (int i = r; i >= l; i--)
        {
            if (arr[i - 1] > arr[i])
            {
                switchHappened = true;
                swap(arr[i - 1], arr[i]);
            }
        }
        l++;
        r--;
    } while (switchHappened && l <= r);
    print_each_element(arr);
    return 0;
}