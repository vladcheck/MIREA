import os
import time
from typing import Callable
from algorithms import *
from plots import *
import psutil
import gc  # Импортируем garbage collector

# Параметр: количество прогонов для усреднения
NUM_RUNS = 3

small_test_values = [100, 1000]
large_test_values = [1_000_000, 1_000_000_000]


def measure_time_and_memory(func: Callable[[int], List[int]], n: int) -> tuple:
    """
    Измеряет среднее время выполнения и максимальное потребление памяти за NUM_RUNS прогонов.
    Возвращает: (среднее время в секундах, количество простых чисел, максимальная память в МБ, ошибка)
    """
    process = psutil.Process(os.getpid())
    times = []
    mem_diffs = []
    error_occurred = None
    primes = []

    for _ in range(NUM_RUNS):
        # Принудительно запускаем сборку мусора перед каждым измерением
        gc.collect()

        # Запоминаем память до выполнения
        mem_before = process.memory_info().rss / 1024 / 1024  # МБ

        start_time = time.perf_counter()
        try:
            primes = func(n)
        except Exception as e:
            # Если произошла ошибка, возвращаем её
            error_occurred = str(e)
            # Возвращаем значения по умолчанию для ошибки
            return float("inf"), 0, 0, error_occurred

        end_time = time.perf_counter()
        # Запоминаем память после выполнения
        mem_after = process.memory_info().rss / 1024 / 1024  # МБ

        # Сохраняем время и разницу памяти для этого прогона
        times.append(end_time - start_time)
        mem_diffs.append(mem_after - mem_before)

    # Принудительно запускаем сборку мусора после всех прогонов
    gc.collect()

    if error_occurred:
        return float("inf"), 0, 0, error_occurred

    # Вычисляем среднее время и максимальную разницу памяти
    avg_time = sum(times) / len(times)
    max_mem_diff = max(mem_diffs)
    # Количество простых чисел можно взять из последнего прогона
    count = len(primes)

    return avg_time, count, max_mem_diff, None


def main():
    if not os.path.exists("dist"):
        os.mkdir("dist")  # Исправлен путь: убран начальный слэш

    # Словарь: название -> функция
    algorithms = {
        "Обычное решето": sieve_of_eratosthenes,
        "Сегментированное": segmented_sieve,
        "Гибридное": hybrid_optimized_sieve,
        "Битовое (оптимиз. память)": bitarray_sieve,
        "Решето Аткина": atkin_sieve,
    }

    print("=== Сравнение алгоритмов поиска простых чисел (Малые n) ===\n")
    print(
        f"{'Алгоритм':<25} | {'Время (с)':>10} | {'Простых':>8} | {'Память (МБ)':>11}"
    )
    print("-" * 80)

    all_results_small = []  # Список для хранения результатов малых n
    for n in small_test_values:
        print(f"\nn = {n:,}")
        print("-" * 80)

        current_round_results = []
        for name, func in algorithms.items():
            time_taken, count, mem, error = measure_time_and_memory(func, n)
            if error:
                result_tuple = (n, name, "ERROR", 0, 0, error)
                current_round_results.append(result_tuple)
                print(f"  {name:<25} | {'ОШИБКА':>10} | {'—':>8} | {'—':>11}")
            else:
                result_tuple = (n, name, time_taken, count, mem, None)
                current_round_results.append(result_tuple)
                print(f"  {name:<25} | {time_taken:>10.4f} | {count:>8} | {mem:>11.2f}")

        # Находим лучший по времени для текущего n
        valid_results = [
            r for r in current_round_results if isinstance(r[2], (int, float))
        ]
        if valid_results:
            best = min(valid_results, key=lambda x: x[2])
            print(f"  → Быстрее всего: {best[1]} ({best[2]:.4f} с)")

        all_results_small.extend(current_round_results)

    # Построение графиков для малых n
    if all_results_small:
        create_time_plot(all_results_small, "dist/time_small.png")
        print("\nГрафики для малых n сохранены: dist/time_small.png")

    print("\n\n=== Сравнение алгоритмов поиска простых чисел (Большие n) ===\n")
    print(
        f"{'Алгоритм':<25} | {'Время (с)':>10} | {'Простых':>8} | {'Память (МБ)':>11}"
    )
    print("-" * 80)

    all_results_large = []  # Список для хранения результатов больших n
    for n in large_test_values:
        print(f"\nn = {n:,}")
        print("-" * 80)

        current_round_results = []
        for name, func in algorithms.items():
            time_taken, count, mem, error = measure_time_and_memory(func, n)
            if error:
                result_tuple = (n, name, "ERROR", 0, 0, error)
                current_round_results.append(result_tuple)
                print(f"  {name:<25} | {'ОШИБКА':>10} | {'—':>8} | {'—':>11}")
            else:
                result_tuple = (n, name, time_taken, count, mem, None)
                current_round_results.append(result_tuple)
                print(f"  {name:<25} | {time_taken:>10.4f} | {count:>8} | {mem:>11.2f}")

        # Находим лучший по времени для текущего n
        valid_results = [
            r for r in current_round_results if isinstance(r[2], (int, float))
        ]
        if valid_results:
            best = min(valid_results, key=lambda x: x[2])
            print(f"  → Быстрее всего: {best[1]} ({best[2]:.4f} с)")

        all_results_large.extend(current_round_results)

    # Построение графиков для больших n
    if all_results_large:
        create_memory_plot(all_results_large, "dist/memory.png")
        create_time_plot(all_results_large, "dist/time_large.png")
        print("\nГрафики для больших n сохранены: dist/memory.png, dist/time_large.png")

    print("\nГотово!")


if __name__ == "__main__":
    main()
