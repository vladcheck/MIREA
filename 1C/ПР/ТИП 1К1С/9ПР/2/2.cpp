#include <iostream>
#include <string>
#include <algorithm>
#include <fstream>
#include <vector>
using namespace std;

int main()
{
    ifstream f1{"2copy.txt"}, f2{"2original.txt"};
    string input1, input2;
    getline(f1, input1);
    getline(f2, input2);
    int index = input2.find(input1);
    bool res = index != string::npos && (index + 1 == input2.size() || input2[index + 1] == ' ');
    cout << ((res) ? "yes" : "no") << endl;
    return 0;
}