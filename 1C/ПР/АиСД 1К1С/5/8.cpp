#include <iostream>
#include <vector>
#include <random>
#include <chrono>
using namespace std;

void print_each_element(vector<int> arr)
{
    for (auto n : arr)
    {
        cout << n << " ";
    }
}

vector<int> insertionSort(vector<int> arr)
{
    for (int i = 1; i < arr.size(); i++)
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
    return arr;
}

vector<int> modifiedInsertionSort(vector<int> arr)
{
    for (int i = 1; i < arr.size(); i++)
    {
        int L = arr[i];
        int left = 0;
        int right = i - 1;

        while (left <= right)
        {
            int mid = (left + right) / 2;
            if (L < arr[mid])
            {
                right = mid - 1;
            }
            else
            {
                left = mid + 1;
            }
        }
        arr.insert(arr.begin() + left, L);
        arr.erase(arr.begin() + i + 1);
    }

    return arr;
}

int main()
{
    srand(time(NULL));

    vector<int> arr;
    for (int i = 0; i < 1000; i++)
    {
        arr.push_back(rand() % 1000);
    }

    auto begin = chrono::steady_clock::now();
    insertionSort(arr);
    auto end = chrono::steady_clock::now();
    double duration = chrono::duration_cast<chrono::nanoseconds>(end - begin).count();
    cout << "Time taken by insertionSort() to sort 1000 elements: " << duration << " nanoseconds" << endl;

    begin = chrono::steady_clock::now();
    modifiedInsertionSort(arr);
    end = chrono::steady_clock::now();
    duration = chrono::duration_cast<chrono::nanoseconds>(end - begin).count();
    cout << "Time taken by modifiedInsertionSort() to sort 1000 elements: " << duration << " nanoseconds" << endl;
    return 0;
}