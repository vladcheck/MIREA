#include "Hash.h"

HashTable<std::string,std::string> get_table_of_sums(std::vector<int>& v) {
    HashTable<std::string,std::string> *tb = new HashTable<std::string,std::string>();
    for (int i = 0; i < v.size(); i++) {
        for (int j = i+1; j < v.size(); j++) {
            std::string sum = std::to_string(v[i]+v[j]);
            std::string indexes = std::to_string(i) + " " + std::to_string(j);
            tb->add(Entry{sum,indexes});
        }
    }
    return *tb;
}

int main(int argc, char const *argv[])
{
    std::vector<int> vec{-1, 2, 3, 4, 7};
    HashTable tb = get_table_of_sums(vec);
    tb.print();
    return 0;
}

