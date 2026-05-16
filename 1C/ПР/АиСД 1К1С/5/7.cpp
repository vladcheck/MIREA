#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
using namespace std;

vector<int> bubbleSort(vector<int> arr)
{
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
    return arr;
}

vector<int> shakerSort(vector<int> arr)
{
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
    return arr;
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

vector<int> selectionSort(vector<int> arr)
{
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
    return arr;
}

vector<int> shellSort(vector<int> arr)
{
    for (auto gap : {20, 10, 5, 2, 1})
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
    }
    return arr;
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

vector<int> small = {3, 1, 6, 7, 10, 3, 5, 2, 0, 20, 4, 5, 8};
vector<int> big = {8, 131, 198, 169, 123, 71, 81, 16, 90, 155, 120, 46, 152, 77, 50, 67, 55, 82, 145, 6, 190, 156, 121, 107, 111, 129, 20, 187, 72, 51, 63, 143, 1, 166, 39, 168, 134, 160, 144, 69, 86, 140, 93, 146, 58, 98, 43, 102, 91, 181, 182, 200, 78, 194, 45, 61, 47, 34, 154, 186, 110, 191, 19, 172, 83, 126, 87, 22, 31, 49, 178, 133, 12, 165, 56, 114, 141, 33, 84, 176, 28, 162, 65, 35, 177, 161, 37, 10, 199, 94, 17, 173, 13, 3, 73, 40, 175, 92, 142, 99, 138, 139, 4, 88, 101, 118, 104, 75, 149, 163, 157, 197, 95, 9, 62, 54, 109, 5, 150, 52, 193, 119, 151, 85, 179, 38, 14, 36, 2, 23, 135, 27, 164, 30, 124, 136, 24, 26, 25, 192, 147, 64, 21, 59, 184, 103, 170, 108, 100, 130, 185, 32, 183, 41, 80, 44, 79, 53, 116, 76, 171, 188, 196, 74, 174, 48, 7, 137, 42, 167, 106, 122, 18, 128, 189, 60, 29, 113, 127, 115, 132, 112, 148, 15, 180, 195, 57, 97, 66, 96, 70, 68, 89, 11, 153, 105, 117, 158, 159, 125};

int main()
{
    // bubbleSort()
    chrono::steady_clock::time_point begin = chrono::steady_clock::now();
    bubbleSort(small);
    chrono::steady_clock::time_point end = chrono::steady_clock::now();
    cout << "Time taken by " << "bubbleSort()" << " to sort " << small.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    begin = chrono::steady_clock::now();
    bubbleSort(big);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "bubbleSort()" << " to sort " << big.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    cout << endl;

    // shakerSort()
    begin = chrono::steady_clock::now();
    shakerSort(small);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "shakerSort()" << " to sort " << small.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    begin = chrono::steady_clock::now();
    shakerSort(big);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "shakerSort()" << " to sort " << big.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    cout << endl;

    // insertionSort()
    begin = chrono::steady_clock::now();
    insertionSort(small);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "insertionSort()" << " to sort " << small.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    begin = chrono::steady_clock::now();
    insertionSort(big);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "insertionSort()" << " to sort " << big.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    cout << endl;

    // selectionSort()
    begin = chrono::steady_clock::now();
    selectionSort(small);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "selectionSort()" << " to sort " << small.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    begin = chrono::steady_clock::now();
    selectionSort(big);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "selectionSort()" << " to sort " << big.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    cout << endl;

    // shellSort()
    begin = chrono::steady_clock::now();
    shellSort(small);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "shellSort()" << " to sort " << small.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    begin = chrono::steady_clock::now();
    shellSort(big);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "shellSort()" << " to sort " << big.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    cout << endl;

    // quickSort()
    begin = chrono::steady_clock::now();
    quickSort(small);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "quickSort()" << " to sort " << small.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    begin = chrono::steady_clock::now();
    quickSort(big);
    end = chrono::steady_clock::now();
    cout << "Time taken by " << "quickSort()" << " to sort " << big.size() << " elements: " << chrono::duration_cast<chrono::nanoseconds>(end - begin).count() << " nanoseconds" << endl;
    cout << endl;

    return 0;
}