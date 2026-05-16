#include <iostream>
#include <vector>
#include <string>
#include <map>
using namespace std;

// аналог произведения строки на число из питона
string mult(int times, string c)
{
    string res;
    for (int i = 0; i < times; i++)
    {
        res = res + c;
    }
    return res;
}

// берем на вход строку, а не int, чтобы не плодить лишнюю переменную
string intToRoman(string num)
{
    vector<string> digits_10 = {"I", "X", "C", "M"};
    vector<string> digits_5 = {"V", "L", "D"};
    string roman = "";
    reverse(num.begin(), num.end());
    for (int i = 0; i < num.size(); i++)
    {
        char d_char = num[i];
        int d = d_char - '0'; // переводим символ в число ("3" => 3)
        if (0 < d && d <= 3)
        {
            roman = mult(d, digits_10[i]) + roman; // просто несколько раз пишем число данного разряда
        }
        else if (d == 4)
        {
            roman = digits_10[i] + digits_5[i] + roman; // число данного разряда (1,10,100) + число данного разряда (5,50,500)
        }
        else if (5 <= d && d <= 8)
        {
            roman = digits_5[i] + mult(d - 5, digits_10[i]) + roman; // число данного разряда (5,50,500) + несколько раз число данного разряда (1,10,100)
        }
        else if (d == 9)
        {
            roman = digits_10[i] + digits_10[i + 1] + roman; // число данного разряда + число следующего разряда (1 и 10 = 9, 10 и 100 = 90)
        }
    }
    return roman;
}

int romanToInt(string num)
{
    map<char, int> values = {{'I', 1}, {'V', 5}, {'X', 10}, {'L', 50}, {'C', 100}, {'D', 500}, {'M', 1000}};
    int conv = 0;

    for (int i = 0; i < num.size(); i++)
    {
        if (i + 1 == num.size()) // уперлись в конец числа
        {
            conv += values.at(num[i]);
        }
        // число из данного разряда численно >= число из следующего разряда
        // напр. 10 и 5, 500 и 100
        else if (values.at(num[i]) >= values.at(num[i + 1]))
        {
            conv += values.at(num[i]);
        }
        // число из данного разряда численно < число из следующего разряда, напр. 1 и 10
        // значит, его нужно вычесть
        else
        {
            conv -= values.at(num[i]);
        }
    }
    return conv;
}

int main()
{
    // Вывод для тестирования
    for (int i = 1000; i <= 2000; i++)
    {
        string roman = intToRoman(to_string(i));
        int back = romanToInt(roman);
        cout << i << " => " << roman << " => " << back << endl;
    }
    return 0;
}