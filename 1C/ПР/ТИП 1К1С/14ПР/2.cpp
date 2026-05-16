#include <string>
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main(int argc, char const *argv[])
{
    // Рандомный текст
    const string data = "Ma famille est petite: moi, ma sœur, ma mère et mon père. Mes parents ont 40 ans. Ma sœur cadète a treize ans et elle s’appelle Arina. Nous avons aussi notre grand-mère,elle a 69 ans et elle s’appelle Klavdia. Nous avons deux animaux, une chatte et une chienne. La chatte s'appelle Nana, elle a 12 ans. La chienne s'appelle Lyusya, elle a 5 ans.";
    const vector<char> forbidden = {',', '.', ':'}; // Запрещённые знаки
    vector<string> words = {""};                    // Все слова
    for (auto c : data)
    {
        // Начать новое слово, если пошёл пробел
        if (c == ' ')
        {
            words.push_back("");
        }
        // Прибавить символ к последнему считываемому "слову" из words
        else if (find(forbidden.begin(), forbidden.end(), c) == forbidden.end())
        {
            words[words.size() - 1] += char(tolower(c));
        }
    }
    vector<string> unique_words = {};

    for (auto word : words)
    {
        // Если слово ещё не появлялось в векторе - добавляем его
        if (find(unique_words.begin(), unique_words.end(), word) == unique_words.end())
        {
            unique_words.push_back(word);
        }
    }
    for (auto word : unique_words)
    {
        cout << word << endl;
    }
    return 0;
}
