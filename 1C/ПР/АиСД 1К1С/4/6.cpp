#include <iostream>
using namespace std;

void tower(int n, char from_rod, char to_rod,
           char helper_rod)
{
    if (n == 0)
    {
        return;
    }
    tower(n - 1, from_rod, helper_rod, to_rod);
    cout << "Move disk " << n << " from rod " << from_rod
         << " to rod " << to_rod << endl;
    tower(n - 1, helper_rod, to_rod, from_rod);
}

int main()
{
    tower(3, 'A', 'B', 'C');
    return 0;
}
