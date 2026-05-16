#include <vector>
#include <algorithm>
#include <iostream>

int index_by_value(int value, std::vector<std::vector<int>> &hash) {
    auto * vec = &hash[value % hash.size()];
    return (std::count(vec->begin(),vec->end(),value) == 1) ? value % hash.size() : -1;
}

int hash_function(int n) {
    return n % 7;
}

void fill_hash_table(std::vector<int> &vec, std::vector<std::vector<int>> &hash) {
    for (int n : vec) {
        if (std::count(hash[hash_function(n)].begin(),hash[hash_function(n)].end(),n) == 0) {
            hash[hash_function(n)].push_back(n);
        }
    }
}

void print_hash_table(std::vector<std::vector<int>> &hash) {
    for (int i = 0; i < hash.size();i++) {
        std::cout << i << ": ";
        for (auto n : hash[i]) {
            std::cout << n << " ";
        } 
        std::cout << std::endl;
    }
}

int main(int argc, char const *argv[])
{
    std::vector<std::vector<int>> hash(7);
    std::vector<int> vec{86, 90, 27, 29, 38, 30, 40, 30};

    fill_hash_table(vec,hash);
    print_hash_table(hash);

    std::cout << std::endl << index_by_value(40, hash) << std::endl; // 5
    std::cout << index_by_value(3, hash) << std::endl; // -1 - такого числа нет в таблице
    return 0;
}
