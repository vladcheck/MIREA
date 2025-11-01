import matplotlib.pyplot as plt
from logging import Logger, getLogger
from typing import List, Tuple, Dict, Any
import numpy as np

logger: Logger = getLogger("plotting")


def _organize_results(results: List[Tuple]) -> Dict[str, Dict[int, Any]]:
    organized = {}
    for result in results:
        if len(result) != 6:
            logger.warning(
                f"Unexpected result tuple length: {len(result)}, skipping: {result}"
            )
            continue

        n, alg_name, time_val, count, mem_val, error = result

        if error is not None:
            # Skip results with errors
            continue

        if alg_name not in organized:
            organized[alg_name] = {}

        # Use time in milliseconds, memory in KB as per original intention in plots.py
        organized[alg_name][n] = {
            "time_ms": time_val * 1000 if isinstance(time_val, (int, float)) else 0,
            "memory_kb": mem_val * 1024 if isinstance(mem_val, (int, float)) else 0,
            "count": count,
        }
    return organized


def create_time_plot(results: List[Tuple], filename: str) -> None:
    organized_results = _organize_results(results)
    if not organized_results:
        logger.warning("No valid results to plot for time.")
        return

    plt.figure(figsize=(12, 7))

    for alg_name, data in organized_results.items():
        # Sort by n to ensure correct plotting order
        sorted_items = sorted(data.items())
        n_values, metrics = zip(*sorted_items) if sorted_items else ([], [])
        times_ms = [m["time_ms"] for m in metrics]

        plt.plot(
            list(n_values),
            times_ms,
            label=alg_name,
            marker="o",
            linewidth=2,
        )

    plt.title("Время выполнения алгоритмов", fontsize=14, fontweight="bold")
    plt.ylim(bottom=0)
    plt.xlabel("Число n", fontsize=12)
    plt.ylabel("Время (мс)", fontsize=12)
    plt.legend(loc="upper left", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.xscale("log")  # логарифмическая шкала — лучше для больших n
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    logger.info(f"График времени сохранён: {filename}")


def create_memory_plot(results: List[Tuple], filename: str) -> None:
    organized_results = _organize_results(results)
    if not organized_results:
        logger.warning("No valid results to plot for memory.")
        return

    plt.figure(figsize=(12, 7))

    for alg_name, data in organized_results.items():
        sorted_items = sorted(data.items())
        n_values, metrics = zip(*sorted_items) if sorted_items else ([], [])
        mem_kb = [m["memory_kb"] for m in metrics]

        plt.plot(
            list(n_values),
            mem_kb,
            label=alg_name,
            marker="s",
            linewidth=2,
        )

    plt.title("Потребление памяти алгоритмов", fontsize=14, fontweight="bold")
    plt.xlabel("Число n", fontsize=12)
    plt.ylabel("Память (КБ)", fontsize=12)
    plt.legend(loc="upper left", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.xscale("log")
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    logger.info(f"График памяти сохранён: {filename}")
