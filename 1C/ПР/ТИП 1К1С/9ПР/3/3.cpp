#include <iostream>
#include <string>
#include <algorithm>
#include <fstream>
#include <vector>
using namespace std;

string bin(int n)
{
  string res;
  while (n != 0)
  {
    res = to_string(n % 2) + res;
    n /= 2;
  }
  return res;
}

int main()
{
  ifstream input{"input.txt"};
  ofstream output{"output.txt"};
  string text, num;
  getline(input, text);
  cout << text;
  for (int i = 0; i < text.size(); i++)
  {
    if (text[i] >= '0' && text[i] <= '9')
    {
      num += text[i];
    }
    else
    {
      if (num != "")
      {
        output << bin(stoi(num));
      }
      num = "";
      output << text[i];
    }
  }
  if (num != "")
  {
    output << bin(stoi(num));
  }
  return 0;
}