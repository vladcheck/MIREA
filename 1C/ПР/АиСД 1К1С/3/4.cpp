#include "./header files/utils.h"
using namespace std;

vector<int> multiply_vector_by_int(vector<int> vec, int n)
{
    vector<int> res;
    int left = 0;
    for (int i = vec.size() - 1; i >= 0; i--)
    {
        res.insert(res.begin(), vec[i] * n % 10 + left);
        left = vec[i] * n / 10;
    }
    return res;
}

vector<vector<int>> get_addition_rows(vector<int> a, vector<int> b)
{
    vector<vector<int>> res;
    for (auto d : b)
    {
        res.push_back(multiply_vector_by_int(a, d));
    }
    reverse(res.begin(), res.end());
    for (int i = 0; i < res.size(); i++)
    {
        for (int j = 0; j < i; j++)
        {
            res[i].push_back(0);
        }
    }
    for (int i = 0; i < res.size(); i++)
    {
        while (res[i].size() < res.back().size())
        {
            res[i].insert(res[i].begin(), 0);
        }
    }
    return res;
}

vector<int> add_vectors(vector<vector<int>> vecs)
{
    vector<int> res;
    int left = 0;
    for (int i = vecs.back().size() - 1; i >= 0; i--)
    {
        int sum = 0;
        for (auto vec : vecs)
        {
            sum += vec[i];
        }
        res.insert(res.begin(), (sum + left) % 10);
        left = (sum + left) / 10;
    }
    return res;
}

string get_rid_of_minus(string a)
{
    return (a[0] == '-') ? a.substr(1, a.size() - 2) : a;
}

string mult(string a, string b)
{
    if (a == "0" || b == "0")
        return "0";
    bool negative = (a[0] == '-' && b[0] != '-') || (a[0] != '-' && b[0] == '-');
    a = get_rid_of_minus(a);
    b = get_rid_of_minus(b);

    vector<int> top = split(a);
    vector<int> bottom = split(b);
    tie(top, bottom) = even_out(top, bottom);
    vector<vector<int>> addition_rows = get_addition_rows(top, bottom);
    string res = list_to_str(add_vectors(addition_rows));
    return (negative) ? "-" + res : res;
}

int main()
{
    cout << mult("-123414241221567890", "987654321") << endl;
    return 0;
}
