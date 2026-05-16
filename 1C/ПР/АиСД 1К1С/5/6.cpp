#include <iostream>
#include <vector>
using namespace std;

void print_each_element(vector<int> arr)
{
    for (auto n : arr)
    {
        cout << n << " ";
    }
}

vector<int> concat(vector<int> a, vector<int> b)
{
    for (auto n : b)
    {
        a.push_back(n);
    }
    return a;
}

vector<int> quickSort(vector<int> arr)
{
    if (arr.size() <= 1)
        return arr;
    int pivot = arr[0];
    vector<int> smaller, equal, larger;
    for (int i = 1; i < arr.size(); i++)
    {
        int n = arr[i];
        if (n == pivot)
            equal.push_back(n);
        else if (n < pivot)
            smaller.push_back(n);
        else
            larger.push_back(n);
    }
    vector<int> res = concat(quickSort(smaller), equal);
    res.push_back(pivot);
    res = concat(res, quickSort(larger));
    return res;
}

int main()
{
    const vector<int> shell_sort_gaps = {10, 5, 2, 1};
    vector<int> arr = {3, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0};
    print_each_element(arr);
    cout << "\n\n";
    arr = quickSort(arr);
    print_each_element(arr);
    return 0;
}