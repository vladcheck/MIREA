import os
from algorithms import *
from benchmark import run_benchmarks
from plots import *
from logging import INFO, Logger, getLogger, basicConfig

logger: Logger = getLogger("main")


def analyze_results(large_results: list[Result]) -> None:
    atkin_wins = 0
    optimized_wins = 0
    eratosthenes_wins = 0

    for r in large_results:
        times: list[int] = [r["EratosthenesMs"], r["AtkinMs"], r["OptimizedMs"]]
        min_time: int = min(times)
        if times[0] == min_time:
            eratosthenes_wins += 1
        elif times[1] == min_time:
            atkin_wins += 1
        else:
            optimized_wins += 1

    logger.info("\nРезультаты на больших числах (10,000-10,000,000):")
    logger.info(f"   - Классический Эратосфен: {eratosthenes_wins} побед")
    logger.info(f"   - Аткин:               {atkin_wins} побед")
    logger.info(f"   - Оптимизированный:       {optimized_wins} побед")

    last_result: Result = large_results[-1]
    logger.info(f"\nНа максимальном n={last_result['N']}:")
    logger.info(
        f"   - Классический:     {last_result['EratosthenesMs']:.2f} мс (базис)"
    )
    logger.info(
        f"   - Аткин:         {last_result['AtkinMs']:.2f} мс ({last_result['Ratio']:.2f}x)"
    )
    logger.info(
        f"   - Оптимизированный: {last_result['OptimizedMs']:.2f} мс ({last_result['OptRatio']:.2f}x)"
    )

    times = [
        last_result["EratosthenesMs"],
        last_result["AtkinMs"],
        last_result["OptimizedMs"],
    ]
    min_time = min(times)
    winner_idx: int = times.index(min_time)
    winner_names: list[str] = [
        "Классический Эратосфен",
        "Аткин",
        "Оптимизированный Эратосфен",
    ]
    winner_name: str = winner_names[winner_idx]
    improvement: float = (
        (last_result["EratosthenesMs"] - min_time) / last_result["EratosthenesMs"]
    ) * 100
    logger.info(f" Победитель: {winner_name} (быстрее на {improvement:.1f}%)")


if __name__ == "__main__":
    if os.path.exists("log.log"):
        os.remove("log.log")
    basicConfig(filename="log.log", level=INFO, encoding="utf8", force=True)

    logger.info("")
    logger.info("Бенчмарк алгоритмов поиска простых чисел")
    logger.info("- Решето Эратосфена")
    logger.info("- Решето Аткина")
    logger.info("- Оптимизированное решето Эратосфена")

    small_results, large_results = run_benchmarks()

    logger.info("")
    logger.info("Создание графиков")
    create_time_plot(small_results, "Малые диапазоны (100 - 10,000)", "small_range.png")
    create_time_plot(
        large_results, "Большие диапазоны (10,000 - 10,000,000)", "large_range.png"
    )
    create_ratio_plot(small_results, "ratio_small.png")
    create_ratio_plot(large_results, "ratio_large.png")
    logger.info("")
    logger.info("Все графики успешно созданы!")

    analyze_results(large_results)
