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
    cout << endl;
}

void insertionSort(vector<int> &arr)
{
    for (int i = 1; i < arr.size(); i++)
    {
        if (arr[i] < arr[i - 1])
        {
            int key = arr[i];
            int j = i - 1;
            while (j >= 0 && arr[j] > key)
            {
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = key;
        }
    }
}

int main()
{
    vector<int> arr{10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0};
    print_each_element(arr);
    cout << "\n";
    insertionSort(arr);
    print_each_element(arr);
    return 0;
}