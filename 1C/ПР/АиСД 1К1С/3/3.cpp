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

string sum10(string a, string b)
{
    vector<int> aVec = split(a);
    vector<int> bVec = split(b);
    int lenMax = max(aVec.size(), bVec.size()) + 1;
    tie(aVec, bVec) = even_out(aVec, bVec);
    while (count(bVec.begin(), bVec.end(), 0) != bVec.size())
    {
        vector<int> sum(lenMax, 0);
        vector<int> add(lenMax, 0);
        for (int i = lenMax - 1; i >= 0; i--)
        {
            int total = aVec[i] + bVec[i];
            if (total >= 10)
            {
                add[i - 1] = 1;
            }
            sum[i] = total % 10;
        }
        print_step(sum, add);
        aVec = sum;
        bVec = add;
    }
    return list_to_str(aVec);
}

int main()
{
    cout << sum10("99999999999999999931994212149999999999", "88888888888881111111111111883159943288888888") << endl;
    return 0;
}
