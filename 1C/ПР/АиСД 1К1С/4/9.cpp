#include "Hash.h"

int main(int argc, char const *argv[])
{
    std::string str = "Huh? What the?????";
    HashTable tb = HashTable<char,int>();
    for (char c : str) {
        if (!tb.has_key(c)) {
            tb.add(Entry<char,int>(c,1));
        }
        else
        {
            int amount = tb.retrieve(c)[0];
            tb.remove(Entry<char,int>(c,amount));
            tb.add(Entry<char,int>(c,amount+1));
        }
    }
    tb.print();
    return 0;
}
