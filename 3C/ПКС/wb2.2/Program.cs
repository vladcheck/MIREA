Console.OutputEncoding = System.Text.Encoding.UTF8;
Matrix matrixA = new(0, 0);
Matrix matrixB = new(0, 0);

PrintInstructions();
while (true)
{
    try
    {
        int choice = Getters.TryGetInt("операцию");

        switch (choice)
        {
            case 0:
                Environment.Exit(0);
                break;
            case 1:
                matrixA = CreateMatrix("A");
                break;
            case 2:
                matrixB = CreateMatrix("B");
                break;
            case 3:
                ShowMatrices(matrixA, matrixB);
                break;
            case 4:
                AddMatrices(matrixA, matrixB);
                break;
            case 5:
                MultiplyMatrices(matrixA, matrixB);
                break;
            case 6:
                Det(matrixA, "A");
                break;
            case 7:
                Det(matrixB, "B");
                break;
            case 8:
                matrixA = Inverse(matrixA, "A");
                break;
            case 9:
                matrixB = Inverse(matrixB, "B");
                break;
            case 10:
                matrixA = T(matrixA, "A");
                break;
            case 11:
                matrixB = T(matrixB, "B");
                break;
            case 12:
                SolveSystem(matrixA, matrixB);
                break;
            case 13:
                PrintInstructions();
                break;
            default:
                Console.WriteLine("Неверный выбор!");
                break;
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Ошибка: {ex.Message}");
    }
}

static void PrintInstructions()
{
    Console.WriteLine("\n========== КАЛЬКУЛЯТОР МАТРИЦ ==========");
    Console.WriteLine("1. Создать матрицу A");
    Console.WriteLine("2. Создать матрицу B");
    Console.WriteLine("3. Показать матрицы");
    Console.WriteLine("4. Сложение матриц (A + B)");
    Console.WriteLine("5. Умножение матриц (A * B)");
    Console.WriteLine("6. Определитель матрицы A");
    Console.WriteLine("7. Определитель матрицы B");
    Console.WriteLine("8. Обратная матрица A");
    Console.WriteLine("9. Обратная матрица B");
    Console.WriteLine("10. Транспонирование матрицы A");
    Console.WriteLine("11. Транспонирование матрицы B");
    Console.WriteLine("12. Решение системы уравнений (A * X = B)");
    Console.WriteLine("13. Вывести эту инструкцию");
    Console.WriteLine("0. Выход");
}

static Matrix CreateMatrix(string name)
{
    int n = Getters.TryGetInt($"количество строк матрицы {name}");
    int m = Getters.TryGetInt($"количество столбцов матрицы {name}");

    if (n <= 0 || m <= 0)
    {
        throw new ArgumentException("Размерность должна быть положительной!");
    }

    Console.WriteLine("\nВыберите способ заполнения:");
    Console.WriteLine("1. Ввод с клавиатуры");
    Console.WriteLine("2. Случайные числа");
    Console.Write("Ваш выбор: ");
    int fillChoice = Getters.TryGetInt();

    Matrix matrix = new(n, m);

    if (fillChoice == 1)
    {
        matrix.FillManually();
    }
    else if (fillChoice == 2)
    {
        double a = Getters.TryGetDouble("минимальное значение диапазона (a)");
        double b = Getters.TryGetDouble("максимальное значение диапазона (b)");
        matrix.FillRandom(a, b);
    }
    else
    {
        throw new ArgumentException("Неверный выбор способа заполнения!");
    }

    Console.WriteLine($"\nМатрица {name} создана:");
    matrix.Print();

    return matrix;
}

static void ShowMatrices(Matrix a, Matrix b)
{
    if (a != null)
    {
        Console.WriteLine("\nМатрица A:");
        a.Print();
    }
    else
    {
        Console.WriteLine("\nМатрица A не создана");
    }

    if (b != null)
    {
        Console.WriteLine("\nМатрица B:");
        b.Print();
    }
    else
    {
        Console.WriteLine("\nМатрица B не создана");
    }
}

static void AddMatrices(Matrix a, Matrix b)
{
    if (a == null || b == null)
    {
        throw new InvalidOperationException("Обе матрицы должны быть созданы!");
    }
    Console.WriteLine("Вычисляем...");
    Matrix result = a.Add(b);
    Console.WriteLine("\nРезультат сложения (A + B):");
    result.Print();
}

static void MultiplyMatrices(Matrix a, Matrix b)
{
    if (a == null || b == null)
    {
        throw new InvalidOperationException("Обе матрицы должны быть созданы!");
    }
    Console.WriteLine("Вычисляем...");
    Matrix result = a.Multiply(b);
    Console.WriteLine("\nРезультат умножения (A * B):");
    result.Print();
}

static void Det(Matrix m, string name)
{
    if (m == null)
    {
        throw new InvalidOperationException($"Матрица {name} не создана!");
    }
    Console.WriteLine("Вычисляем...");
    double det = m.Det();
    Console.WriteLine($"\nОпределитель матрицы {name}: {det}");
}

static Matrix Inverse(Matrix m, string name)
{
    if (m == null)
    {
        throw new InvalidOperationException($"Матрица {name} не создана!");
    }
    Console.WriteLine("Вычисляем...");
    Matrix inverse = m.Inverse();
    Console.WriteLine($"\nОбратная матрица {name}:");
    inverse.Print();

    string apply = Getters.TryGetString("Применить? ").ToLowerInvariant();
    if (apply == "y" || apply == "yes" || apply == "да" || apply == "д")
    {
        return inverse;
    }
    else
    {
        return m;
    }
}

static Matrix T(Matrix m, string name)
{
    if (m == null)
    {
        throw new InvalidOperationException($"Матрица {name} не создана!");
    }
    Console.WriteLine("Вычисляем...");
    Matrix transposed = m.T();
    Console.WriteLine($"\nТранспонированная матрица {name}:");
    transposed.Print();
    
    string apply = Getters.TryGetString("Применить? ").ToLowerInvariant();
    if (apply == "y" || apply == "yes" || apply == "да" || apply == "д")
    {
        return transposed;
    }
    else
    {
        return m;
    }
}

static void SolveSystem(Matrix a, Matrix b)
{
    if (a == null || b == null)
    {
        throw new InvalidOperationException("Обе матрицы должны быть созданы!");
    }
    Console.WriteLine("Вычисляем...");
    double[] solution = Matrix.SolveSystem(a, b);
    Console.WriteLine("\nРешение системы уравнений (A * X = B):");
    for (int i = 0; i < solution.Length; i++)
    {
        Console.WriteLine($"x{i + 1} = {solution[i]:F4}");
    }
}

class Getters
{
public static int TryGetInt(string description = "число")
{
    do
    {
        Console.Write($"Введите {description}: ");
        if (Int32.TryParse(Console.ReadLine(), out int result))
        {
            return result;
        }
        else
        {
            Console.WriteLine("Некорректный ввод!");
        }
    } while (true);
}

public static double TryGetDouble(string description = "число")
{
    do
    {
        Console.Write($"Введите {description}: ");
        if (Double.TryParse(Console.ReadLine(), out double result))
        {
            return result;
        }
        else
        {
            Console.WriteLine("Некорректный ввод!");
        }
    } while (true);
}

public static string TryGetString(string description = "")
{
    string? result;
    do
    {
        if (!String.IsNullOrEmpty(description)) Console.Write(description);

        result = Console.ReadLine();
        if (String.IsNullOrEmpty(result))
        {
            Console.WriteLine("Ввод пустой, попробуйте ввести что-нибудь");
        }
        else
        {
            return result;
        }
    } while (true);
}
}


class Matrix(int rows, int cols)
{
private readonly double[,] data = new double[rows, cols];
private readonly int rows = rows;

public int Rows { get; } = rows;
public int Cols { get; } = cols;

public double this[int i, int j]
{
    get => data[i, j];
    set => data[i, j] = value;
}

public void FillManually()
{
    Console.WriteLine("\nВведите элементы матрицы:");
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < Cols; j++)
        {
            Console.Write($"Элемент [{i + 1},{j + 1}]: ");
            data[i, j] = Getters.TryGetDouble();
        }
    }
}

public void FillRandom(double min, double max)
{
    Random rand = new();
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < Cols; j++)
        {
            data[i, j] = rand.NextDouble() * (max - min) + min;
        }
    }
}

public void Print()
{
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < Cols; j++)
        {
            Console.Write($"{data[i, j],10:F2} ");
        }
        Console.WriteLine();
    }
}

public Matrix Add(Matrix other)
{
    if (rows != other.rows || Cols != other.Cols)
    {
        throw new InvalidOperationException(
            $"Невозможно сложить матрицы: размерности не совпадают ({rows}x{Cols} и {other.rows}x{other.Cols})");
    }

    Matrix result = new(rows, Cols);
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < Cols; j++)
        {
            result[i, j] = data[i, j] + other[i, j];
        }
    }
    return result;
}

public Matrix Multiply(Matrix other)
{
    if (Cols != other.rows)
    {
        throw new InvalidOperationException(
            $"Невозможно умножить матрицы: несовместимые размерности ({rows}x{Cols} и {other.rows}x{other.Cols}). " +
            $"Количество столбцов первой матрицы должно равняться количеству строк второй.");
    }

    Matrix result = new(rows, other.Cols);
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < other.Cols; j++)
        {
            double sum = 0;
            for (int k = 0; k < Cols; k++)
            {
                sum += data[i, k] * other[k, j];
            }
            result[i, j] = sum;
        }
    }
    return result;
}

public bool IsSquare()
{
    return Rows == Cols;
}

public double Det()
{
    if (!IsSquare())
    {
        throw new InvalidOperationException(
            $"Невозможно найти определитель: матрица не квадратная ({rows}x{Cols})");
    }

    return Det(data, rows);
}

private static double Det(double[,] matrix, int n)
{
    if (n == 1)
        return matrix[0, 0];

    if (n == 2)
        return matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0];

    double det = 0;
    for (int j = 0; j < n; j++)
    {
        det += Math.Pow(-1, j) * matrix[0, j] * Det(Minor(matrix, 0, j, n), n - 1);
    }
    return det;
}

private static double[,] Minor(double[,] matrix, int row, int col, int n)
{
    double[,] minor = new double[n - 1, n - 1];
    int mi = 0;

    for (int i = 0; i < n; i++)
    {
        if (i == row) continue;
        int mj = 0;

        for (int j = 0; j < n; j++)
        {
            if (j == col) continue;
            minor[mi, mj] = matrix[i, j];
            mj++;
        }
        mi++;
    }
    return minor;
}

    public Matrix T()
    {
        Matrix result = new(Cols, Rows);
        for (int i = 0; i < rows; i++)
        {
            for (int j = 0; j < Cols; j++)
            {
                result[j, i] = data[i, j];
            }
        }
        return result;
    }

public Matrix Inverse()
{
    if (rows != Cols)
    {
        throw new InvalidOperationException(
            $"Невозможно найти обратную матрицу: матрица не квадратная ({rows}x{Cols})");
    }

    double det = Det();
    if (Math.Abs(det) < 1e-10)
    {
        throw new InvalidOperationException(
            "Невозможно найти обратную матрицу: определитель равен нулю");
    }

    Matrix cofactors = new(rows, Cols);
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < Cols; j++)
        {
            double minor = Det(Minor(data, i, j, rows), rows - 1);
            cofactors[i, j] = Math.Pow(-1, i + j) * minor;
        }
    }

    Matrix adjugate = cofactors.T();
    Matrix inverse = new(rows, Cols);
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < Cols; j++)
        {
            inverse[i, j] = adjugate[i, j] / det;
        }
    }

    return inverse;
}

private static double[] Kramer(Matrix a, Matrix b, double aDet)
{
    double[] solution = new double[a.rows];
    for (int i = 0; i < a.rows; i++)
    {
        Matrix temp = new(a.rows, a.Cols);
        for (int row = 0; row < a.rows; row++)
        {
            for (int col = 0; col < a.Cols; col++)
            {
                if (col == i)
                    temp[row, col] = b[row, 0];
                else
                    temp[row, col] = a[row, col];
            }
        }
        solution[i] = temp.Det() / aDet;
    }
    return solution;
}

public static double[] SolveSystem(Matrix a, Matrix b)
{
    if (a.rows != a.Cols)
    {
        throw new InvalidOperationException(
            $"Система не может быть решена: матрица коэффициентов не квадратная ({a.rows}x{a.Cols})");
    }

    if (b.Cols != 1)
    {
        throw new InvalidOperationException(
            $"Матрица B должна быть вектором-столбцом (иметь 1 столбец), получено: {b.Cols} столбцов");
    }

    if (a.rows != b.rows)
    {
        throw new InvalidOperationException(
            $"Несовместимые размерности: A({a.rows}x{a.Cols}) и B({b.rows}x{b.Cols})");
    }

    double aDet = a.Det();
    if (Math.Abs(aDet) < 1e-10)
    {
        throw new InvalidOperationException(
            "Система не имеет однозначного решения: определитель матрицы коэффициентов равен нулю");
    }

    return Kramer(a,b,aDet);
}

}
