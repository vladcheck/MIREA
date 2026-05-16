#include "./header files/utils.h"
using namespace std;

void print_vector(vector<int> &vec)
{
    for (auto el : vec)
    {
        cout << el << " ";
    }
    cout << endl;
}

void print_step(vector<int> &sum, vector<int> &add)
{
    print_vector(sum);
    print_vector(add);
    cout << endl;
}

string sum(string a, string b)
{
    vector<int> aVec = split(a);
    vector<int> bVec = split(b);
    int lenMax = max(aVec.size(), bVec.size()) + 1;
    tie(aVec, bVec) = even_out(aVec, bVec);
    while (count(bVec.begin(), bVec.end(), 1) > 0)
    {
        vector<int> sum(lenMax, 0);
        vector<int> add(lenMax, 0);
        for (int i = 1; i < lenMax; i++)
        {
            int total = aVec[aVec.size() - i] + bVec[bVec.size() - i];
            if (total == 2)
            {
                add[add.size() - i - 1] = 1;
            }
            else if (total == 1)
            {
                sum[sum.size() - i] = 1;
            }
        }
        print_step(sum, add);
        aVec = sum;
        bVec = add;
    }
    return list_to_str(aVec);
}

int main()
{
    cout << sum("1010000000000010011111111100101010101011011010", "1111110000000001010100001011010011001") << endl;
    return 0;
}
