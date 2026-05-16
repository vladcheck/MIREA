#include <vector>
using namespace std;

template <typename T>
class Stack
{
    vector<T> data = {};

public:
    void push(T value)
    {
        this->data.push_back(value);
    }

    T pop()
    {
        const T val = this->data.back();
        this->data.pop_back();
        return val;
    }

    bool isEmpty()
    {
        return this->data.size() == 0;
    }
};
