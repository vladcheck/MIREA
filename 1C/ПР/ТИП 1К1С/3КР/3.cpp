#include <iostream>
#include <string>

bool is_palindrome(std::string *s)
{
    int str_len = s->size();
    // одновременный проход с начала строки к ее середине
    // и с конца к середине
    for (int i = 0; i < (int)(str_len / 2); i++)
    {
        // если i-ый элемент отличается от i-ого с конца,
        // то строка - не полиндром
        if (s->at(i) != s->at(str_len - i - 1))
            return false;
    }
    return true;
}

int main(int argc, char const *argv[])
{
    std::string s;
    std::cin >> s;
    std::cout << is_palindrome(&s) << std::endl;
    return 0;
}
