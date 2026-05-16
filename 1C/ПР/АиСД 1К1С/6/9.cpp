#include <iostream>
#include <fstream>
#include <string>
#include <stack>

void read_file(std::stack<char> *st, std::ifstream *file)
{
    std::string line;
    while (std::getline(*file, line))
    {
        for (char c : line)
        {
            st->push(c);
        }
    }
    file->close();
}

int main()
{
    std::ifstream file{"9.txt"};
    std::stack<char> st;

    if (file.is_open())
    {
        read_file(&st, &file);
        while (st.size())
        {
            std::cout << st.top();
            st.pop();
        }
    }
    else
    {
        std::cerr << "Can't open the file!" << std::endl;
        return 1;
    }
    return 0;
}