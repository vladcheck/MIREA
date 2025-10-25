import time
from typing import Literal
from algorithms import *
from logging import Logger, getLogger
from result import Result

logger: Logger = getLogger("benchmark")


def to_ms(seconds: float) -> float:
    return seconds * 1000


def benchmark(fn, n, iterations=10) -> float:
    total_time = 0
    for _ in range(iterations):
        start: float = time.perf_counter()
        fn(n)
        total_time += time.perf_counter() - start
    avg_time_ms: float = to_ms((total_time / iterations))
    return avg_time_ms


def run_benchmarks() -> tuple[list[Result], list[Result]]:
    small_ranges: list[int] = [100, 500, 1000, 2000, 5000, 10000]
    large_ranges: list[int] = [
        10000,
        50000,
        100000,
        200000,
        500000,
        1000000,
        2000000,
        5000000,
        10000000,
    ]

    small_results: list[dict[str, float]] = []
    large_results: list[dict[str, float]] = []

    logger.info("")
    logger.info("Бенчмарк малых диапазонов")
    logger.info("")
    logger.info(
        f"{'n':<10} | {'Эратосфен':<15} | {'Аткин':<15} | {'Оптимизир.':<15} | {'Лучший':<12}"
    )
    logger.info("-" * 83)
    for n in small_ranges:
        erat_time: float = benchmark(sieve_of_eratosthenes, n, 10)
        atkin_time: float = benchmark(sieve_of_atkin, n, 10)
        optimized_time: float = benchmark(optimized_sieve_of_eratosthenes, n, 10)
        ratio: float = atkin_time / erat_time if erat_time != 0 else float("inf")
        opt_ratio: float = (
            optimized_time / erat_time if erat_time != 0 else float("inf")
        )

        result: dict[str, float] = {
            "N": n,
            "EratosthenesMs": erat_time,
            "AtkinMs": atkin_time,
            "OptimizedMs": optimized_time,
            "Ratio": ratio,
            "OptRatio": opt_ratio,
        }
        small_results.append(result)

        min_time: float = min(erat_time, atkin_time, optimized_time)
        winner = "Эратосфен"
        if atkin_time == min_time:
            winner = "Аткин"
        elif optimized_time == min_time:
            winner = "Оптимизир."

        logger.info(
            f"{n:<10} | {erat_time:<12.5f} мс | {atkin_time:<12.5f} мс | {optimized_time:<12f} мс | {winner}"
        )

    logger.info("")
    logger.info("Бенчмарк больших диапазонов")
    logger.info("")
    logger.info(
        f"{'n':<10} | {'Эратосфен':<15} | {'Аткин':<15} | {'Оптимизир.':<15} | {'Лучший':<12}"
    )
    logger.info("-" * 92)
    for n in large_ranges:
        iterations: Literal[5] | Literal[3] = 5 if n <= 2000000 else 3
        erat_time = benchmark(sieve_of_eratosthenes, n, iterations)
        atkin_time = benchmark(sieve_of_atkin, n, iterations)
        optimized_time = benchmark(optimized_sieve_of_eratosthenes, n, iterations)
        ratio = atkin_time / erat_time if erat_time != 0 else float("inf")
        opt_ratio = optimized_time / erat_time if erat_time != 0 else float("inf")

        result = {
            "N": n,
            "EratosthenesMs": erat_time,
            "AtkinMs": atkin_time,
            "OptimizedMs": optimized_time,
            "Ratio": ratio,
            "OptRatio": opt_ratio,
        }
        large_results.append(result)

        min_time = min(erat_time, atkin_time, optimized_time)
        winner = "Эратосфен"
        if atkin_time == min_time:
            winner = "Аткин"
        elif optimized_time == min_time:
            winner = "Оптимизир."
        improvement = ((erat_time - min_time) / erat_time) * 100

        logger.info(
            f"{n:<10} | {erat_time:<12f} мс | {atkin_time:<11.5f} мс | {optimized_time:<13f} мс | {winner} (+{improvement:.1f}%)",
        )

    return small_results, large_results
