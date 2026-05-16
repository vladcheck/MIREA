#include <iostream>
using namespace std;

void subway(int n, int from_napkin, int to_napkin, int helper_napkin)
{
    // Закончить, если все ингредиенты переложили
    if (n == 0)
    {
        return;
    }
    // Переместить n-1 ингредиент с исходной салфетки на вспомогательную
    subway(n - 1, from_napkin, helper_napkin, to_napkin);
    cout << "Ingredient " << n << " nove from " << from_napkin
         << " to " << to_napkin << endl;
    // Переместить n-1 ингредиент с вспомогательной салфетки на целевую
    subway(n - 1, helper_napkin, to_napkin, from_napkin);
}

int main()
{
    int n;
    cin >> n;
    subway(n, 1, 2, 3);
    return 0;
}