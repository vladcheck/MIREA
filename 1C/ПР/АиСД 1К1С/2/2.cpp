#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm> // Для reverse
using namespace std;

// #1
int max_divisor(int a, int b)
{
    a = abs(a);
    b = abs(b);
    while (a % b != 0)
    {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return b;
}

// #2
// Функция для нахождения простых чисел методом решета Эратосфена
vector<int> eratosfen(int n)
{
    vector<int> primes;

    // Заполняем массив числами от 2 до n
    for (int i = 2; i <= n; i++)
    {
        primes.push_back(i);
    }

    int currentLength = primes.size();
    int previousLength = -1;
    int currIndex = 0;

    // Основной цикл решета Эратосфена
    while (currentLength != previousLength)
    {
        vector<int> newPrimes;

        for (int num : primes)
        {
            if (num % primes[currIndex] != 0 || num == primes[currIndex])
            {
                newPrimes.push_back(num);
            }
        }

        primes = newPrimes;
        previousLength = currentLength;
        currentLength = primes.size();
        currIndex++;
    }

    return primes;
}

// Функция для разложения числа на простые множители
string factor(int n)
{
    vector<int> primes = eratosfen(n);
    reverse(primes.begin(), primes.end());
    string res = "";

    // Цикл по простым числам
    for (int num : primes)
    {
        int divided = 0;

        // Пока число делится на текущий простой множитель
        while (n % num == 0)
        {
            divided++;
            n /= num;
        }

        // Если делитель найден
        if (divided > 0)
        {
            res += to_string(num) + "^" + to_string(divided) + ",";
        }
    }

    // Если не было делений, возвращаем n^1
    res = res.empty() ? to_string(n) + "^1," : res;
    return res.substr(0, res.size() - 1);
}

// #3. Решето Эратосфено взято из II номера
// Вспомогательная функция q_helper
int q_helper(int x, int n, int m)
{
    return (m + x) * (m + x) - n;
}

// Разложение числа на множители методом Ферма
vector<int> factor_by_ferma(int n)
{
    if (n == 1)
    {
        return {};
    }
    vector<int> primes = eratosfen(n);
    if (find(primes.begin(), primes.end(), n) != primes.end())
    {
        return {n};
    }
    if (n % 2 == 0)
    {
        throw invalid_argument("Even numbers are not allowed (" + to_string(n) + ")");
    }

    int m = static_cast<int>(sqrt(n));
    if (m * m == n)
    {
        return {m, m};
    }

    int x = 1;
    int y;
    while (x < n)
    {
        y = q_helper(x, n, m);
        if (static_cast<int>(sqrt(y)) * static_cast<int>(sqrt(y)) == y)
        {
            break;
        }
        x++;
    }

    int B = static_cast<int>(sqrt(y));
    int A = m + x;
    int p = A + B;
    int q = A - B;

    vector<int> res;
    vector<int> p_factors = (find(primes.begin(), primes.end(), p) != primes.end()) ? vector<int>{p} : factor_by_ferma(p);
    vector<int> q_factors = (find(primes.begin(), primes.end(), q) != primes.end()) ? vector<int>{q} : factor_by_ferma(q);

    res.insert(res.end(), p_factors.begin(), p_factors.end());
    res.insert(res.end(), q_factors.begin(), q_factors.end());

    return res;
}

// Функция для красивого вывода результата факторизации
string prettify_ferma(const vector<int> &nums)
{

    string res = "";
    // Уникальные простые множители и их степени
    for (size_t i = 0; i < nums.size(); ++i)
    {
        int count = 1;
        while (i + 1 < nums.size() && nums[i] == nums[i + 1])
        {
            count++;
            i++;
        }
        res += to_string(nums[i]) + "^" + to_string(count) + ",";
    }

    return res.substr(0, res.size() - 1);
}

// #4
// Функция для нахождения n, при котором 2^n - 1 = num

int mersenn(int n)
{
    return pow(2, n) - 1;
}

int get_mersenn_n(int num)
{
    int n = 0;
    while (pow(2, n) - 1 != num)
    {
        n++;
    }
    return n;
}

// Функция Люка-Лемера
int luke_lemer(int k)
{
    if (k == 1)
    {
        return 4;
    }
    else
    {
        return pow(luke_lemer(k - 1), 2) - 2;
    }
}

// Проверка числа Мерсенна
bool check_mersenn(int num)
{
    int n = get_mersenn_n(num);          // Находим n для числа Мерсенна
    return luke_lemer(n - 1) % num == 0; // Проверяем по критерию Люка-Лемера
}

// #5
int neyman(int n)
{
    n *= n;
    string n_str = to_string(n);
    int mid = n_str.length() / 2; // Находим середину строки
    // Извлекаем 5 символов, начиная с mid-2 и заканчивая mid+2
    n = stoi(n_str.substr(mid - 2, 5));
    return n;
}

// #6
vector<int> sundaram(int n)
{
    int upper = floor((n - 1) / 2); // Верхняя граница
    vector<int> primes(upper);      // Массив для простых чисел
    vector<int> indexes;            // Массив для хранения индексов, которые будут исключены

    // Инициализация массива простых чисел
    for (int i = 1; i <= upper; ++i)
    {
        primes[i - 1] = i;
    }

    // Генерация индексов, которые будут исключены
    for (int i = 1; i < n; ++i)
    {
        for (int j = i; j < n; ++j)
        {
            int k = i + j + 2 * i * j;
            if (k <= upper)
            {
                indexes.push_back(k);
            }
            else
            {
                break;
            }
        }
    }

    // Помечаем исключённые индексы как -1
    for (int i = 0; i < indexes.size(); ++i)
    {
        if (indexes[i] <= upper)
        {
            primes[indexes[i] - 1] = -1;
        }
    }

    // Формирование итогового списка простых чисел
    vector<int> result = {2}; // 2 является простым числом
    for (int i = 0; i < primes.size(); ++i)
    {
        if (primes[i] != -1)
        {
            result.push_back(2 * primes[i] + 1); // Преобразуем по формуле 2n + 1
        }
    }

    return result;
}

int main()
{
    while (true)
    {
        int n;
        cin >> n;
        int a, b, c;
        switch (n)
        {
        case 1:
            // #1
            cin >> a >> b >> c;
            cout << max_divisor(a, max_divisor(b, c)) << endl;
            cout << endl;
            break;
        case 2:
            // #2
            cin >> a;
            cout << factor(a) << endl;
            cout << endl;
            break;
        case 3:
            // #3
            cin >> a;
            try
            {
                vector<int> res = factor_by_ferma(a);
                cout << prettify_ferma(res) << endl;
            }
            catch (const exception &e)
            {
                cout << "Не могу" << endl;
            }
            cout << endl;
            break;
        case 4:
            // #4
            cin >> a;
            int m = mersenn(a);
            cout << a << " " << m << endl;
            cout << m << " is Mersenn number: " << (check_mersenn(m) ? "YES" : "NO") << endl;
            cout << endl;
            break;
        case 5:
            // #5
            long seed;
            cin >> seed;

            // Генерация 10 чисел с помощью метода Неймана
            for (int i = 0; i < 10; i++)
            {
                seed = neyman(seed);
                cout << seed << " ";
            }

            cout << "\n\n";
            break;
        case 6:
            // #6
            cin >> a;
            vector<int> primes = sundaram(a);
            // Вывод простых чисел
            for (int prime : primes)
            {
                cout << prime << " ";
            }
            cout << endl;
            break;
        }
    }
    return 0;
}