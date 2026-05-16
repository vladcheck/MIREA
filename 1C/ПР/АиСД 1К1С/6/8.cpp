#include <iostream>
#include <vector>
using namespace std;

void populate_vector(vector<int> *arr, int n)
{
    for (int i = 0; i < n; i++)
    {
        arr->push_back(i);
    }
}

void print_vector(vector<int> *arr)
{
    for (auto n : *arr)
    {
        cout << n << " ";
    }
    cout << endl;
}

void move(vector<int> *arr, int width)
{
    if (width == 0)
        return;
    int length = arr->size();
    if (width > 0)
    {
        for (int i = 0; i < width; i++)
        {
            int last = arr->back();
            arr->pop_back();
            arr->insert(arr->begin(), last);
        }
    }
    else
    {
        for (int i = 0; i < -width; i++)
        {
            int first = arr->front();
            arr->erase(arr->begin());
            arr->push_back(first);
        }
    }
}

int main()
{
    int n = 10;
    vector<int> arr;
    populate_vector(&arr, n);

    cout << "Test move 5 to the right:" << endl;
    print_vector(&arr);
    move(&arr, 5);
    print_vector(&arr);

    cout << "\nTest move 5 to the left:" << endl;
    print_vector(&arr);
    move(&arr, -5);
    print_vector(&arr);

    cout << "\nTest move 12 to the left:" << endl;
    print_vector(&arr);
    move(&arr, -12);
    print_vector(&arr);

    return 0;
}