#include <iostream>
#include <string>
#include <algorithm>
#include <fstream>
#include <vector>
using namespace std;

int main()
{
  ifstream source{"1.txt"};
  ofstream f{"res1.txt"};
  vector<char> banned = {'u', 's', 'e', 'r', 'a', 'g', 'r', 'm', 'n', 't'};
  string input, output;
  getline(source, input);
  for (auto c : input)
  {
    if (count(banned.begin(), banned.end(), c) == 0)
      output += c;
  }
  f << output;
  return 0;
}