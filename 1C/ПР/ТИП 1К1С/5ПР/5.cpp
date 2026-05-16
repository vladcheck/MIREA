// #5: Напишите программу, которая находит пересечение двух множеств.
#include <iostream>
#include <set>

std::set<int> intersection(std::set<int> &set1, std::set<int> &set2)
{
  std::set<int> ans{};
  for (auto n : set1)
  {
    if (set2.find(n) != set2.end())
      ans.insert(n);
  }
  return ans;
}

void set_print(std::set<int> s)
{
  std::cout << "{ ";
  for (auto n : s)
  {
    std::cout << n << " ";
  }
  std::cout << "}";
}

int main()
{
  std::set<int> a = {1, 2, 3, 4, 5, 6, 7};
  std::set<int> b = {5, 3, 6, 7, 8, 9, 10};
  set_print(intersection(a, b));
  return 0;
}
