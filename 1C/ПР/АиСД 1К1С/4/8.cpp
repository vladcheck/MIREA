#include "Hash.h"

void vector_print(std::vector<std::string> vec) {
    if (vec.size() > 0)
    {
        for (auto val : vec) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }
}

int main(int argc, char const *argv[])
{
    HashTable tb = HashTable<std::string,std::string>();
    tb.add(Entry<std::string,std::string>{"John","+777"});
    tb.add(Entry<std::string,std::string>{"Kate","+888"});
    tb.add(Entry<std::string,std::string>{"Kate","+555"});
    tb.add(Entry<std::string,std::string>("Clarice", "+809"));
    tb.print();

    vector_print(tb.retrieve("Kate"));
    vector_print(tb.retrieve("Larry")); // не вернет ничего
    std::cout << std::endl;

    tb.remove(Entry<std::string,std::string>{"Kate","+555"});
    tb.remove(Entry<std::string,std::string>{"John","+555"});
    tb.print();
    return 0;
}
