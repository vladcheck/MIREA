#include <iostream>
#include <fstream>
#include <string>
#include <queue>

bool is_two_digit_int(int n)
{
    return n >= 10;
}

void read_file(std::queue<int> *q, std::ifstream *file)
{
    std::string line;
    std::string curr_num;
    std::vector<int> hold;
    while (std::getline(*file, line))
    {
        for (char c : line)
        {
            std::cout << c;
            if (c == ' ')
            {
                int num = std::stoi(curr_num);
                if (is_two_digit_int(num))
                {
                    hold.push_back(num);
                }
                else
                {
                    q->push(num);
                }
                curr_num = "";
            }
            else
            {
                curr_num += c;
            }
        }
    }
    if (curr_num.size())
    {
        int num = std::stoi(curr_num);
        if (is_two_digit_int(num))
        {
            hold.push_back(num);
        }
        else
        {
            q->push(num);
        }
    }
    std::cout << std::endl;

    while (hold.size())
    {
        q->push(hold.front());
        hold.erase(hold.begin());
    }
}

int main()
{
    std::ifstream file{"10.txt"};
    std::queue<int> q;

    if (file.is_open())
    {
        read_file(&q, &file);
        while (q.size())
        {
            std::cout << q.front() << " ";
            q.pop();
        }
        file.close();
    }
    else
    {
        std::cerr << "Can't open the file!" << std::endl;
        return 1;
    }
    return 0;
}