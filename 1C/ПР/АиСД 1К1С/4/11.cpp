#include "Hash.h"
#include <fstream>
#include <algorithm>

using namespace std;

string trim(string &str) {
    while (str[0] == ' ') {
        str.erase(str.begin());
    }
    while (str[str.size()-1] == ' ') {
        str.erase(str.end());
    }
    return str;
}

HashTable<string,string> parse(string filename) {
    ifstream file{filename};
    if (!file.is_open()) throw;
    
    HashTable<string,string>* hash = new HashTable<string,string>();
    Entry<string,string> *entry = new Entry<string,string>("","");

    for (string line;getline(file,line);)
    {
        line = trim(line);
        if (find(line.begin(),line.end(),':') == line.end()) continue;

        Entry<string,string> *temp = new Entry<string,string>("","");
        bool met_semicolon = false;

        for (auto c : line) {
            if (c == ':') {
                met_semicolon = true;
                continue;
            }
            else if (c == '"' || c == ' ' || c == ',' || c == '\n') continue;
            if (!met_semicolon) {
                temp->key += c;
            } else {
                temp->value += c;
            }
        }
        if (temp->key.compare("name") == 0) {
            entry->key = temp->value;
        }
        else if (temp->key.compare("number") == 0) {
            entry->value = temp->value;
            hash->add(*entry);
            entry->key = "";
            entry->value = "";
        }
    }
    file.close();
    return *hash;
}

int main(int argc, char const *argv[])
{
    HashTable hash = parse("11.json");
    hash.print();
    return 0;
}
