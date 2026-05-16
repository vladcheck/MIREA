#include "stack.h"
#include <iostream>
#include <string>
using namespace std;

bool isCorrect(string &data, Stack<char> st)
{
    int unclosed = 0;
    char val{};
    while (!st.isEmpty())
    {
        val = st.pop();
        if (val == ')')
            unclosed++;
        else
            unclosed--;

        if (unclosed < 0)
            return false;
    }
    return unclosed == 0;
}

int main(int argc, char const *argv[])
{
    string data = "(())()";
    Stack st = Stack<char>();
    for (char ch : data)
    {
        st.push(ch);
    }
    cout << data << endl;
    cout << isCorrect(data, st) << endl;
    return 0;
}
