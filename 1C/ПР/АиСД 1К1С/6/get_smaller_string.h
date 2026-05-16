#include <algorithm>
#include <string>

std::string get_smaller_string(std::string a, std::string b)
{
    if (a.size() < b.size())
        return a;
    else if (a.size() > b.size())
        return b;
    else
    {
        for (int i = 0; i < a.size(); i++)
        {
            int num_a = a[i] - '0';
            int num_b = b[i] - '0';
            if (num_a < num_b)
            {
                return a;
            }
            else if (num_a > num_b)
            {
                return b;
            }
        }
        return NULL;
    }
}
