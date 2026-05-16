#include <iostream>
#include <string>
#include <vector>
using namespace std;

string f(int x, int n)
{
    vector<int> sequence;
    // Преобразуем начальное число x в строку и добавляем каждый символ в вектор
    for (auto d : to_string(x))
    {
        sequence.push_back((int)x);
    }
    // Выполняем n-1 итераций для получения n-го элемента
    for (int i = 0; i < n - 1; i++)
    {
        // Счетчик для подсчета количества повторяющихся цифр
        int count = 1;
        vector<int> new_sequence;
        for (int j = 0; j < sequence.size(); j++)
        {
            // Проверяем, является ли следующая цифра такой же
            if (j + 1 < sequence.size() && sequence[j] == sequence[j + 1])
                count++;
            // Если нет, добавляем в новую последовательность количество повторов и саму цифру
            else
            {
                new_sequence.push_back(count);
                new_sequence.push_back(sequence[j]);
                count = 1;
            }
        }
        sequence = new_sequence;
    }
    string ans = "";
    for (auto d : sequence)
    {
        ans += to_string(d);
    }
    return ans;
}

int main()
{
    int x, n;
    cin >> x >> n;
    cout << f(x, n);
    return 0;
}