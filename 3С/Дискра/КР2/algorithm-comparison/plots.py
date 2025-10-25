import matplotlib.pyplot as plt
from logging import Logger, getLogger
from result import Result

logger: Logger = getLogger("plotting")


def create_time_plot(results: list[Result], title: str, filename: str) -> None:
    n_values: list[int] = [r["N"] for r in results]
    erat_times: list[int] = [r["EratosthenesMs"] for r in results]
    atkin_times: list[int] = [r["AtkinMs"] for r in results]
    optimized_times: list[int] = [r["OptimizedMs"] for r in results]

    plt.figure(figsize=(12, 7))
    plt.plot(
        n_values,
        erat_times,
        label="Эратосфен",
        marker="o",
        color="#3B82F6",
        linewidth=2,
    )
    plt.plot(
        n_values,
        atkin_times,
        label="Аткин",
        marker="s",
        color="#EF4444",
        linewidth=2,
    )
    plt.plot(
        n_values,
        optimized_times,
        label="Оптимизированный",
        marker="^",
        color="#22C55E",
        linewidth=2,
    )

    plt.title(title)
    plt.ylim(bottom=0)
    plt.xlabel("Число (n)")
    plt.ylabel("Время (мс)")
    plt.legend(loc="upper left")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig("dist/" + filename)
    plt.close()
    logger.info(f"✓ График времени: {filename}")


def create_ratio_plot(results: list[Result], filename: str) -> None:
    n_values: list[int] = [r["N"] for r in results]
    atkin_ratios: list[int] = [r["Ratio"] for r in results]
    optimized_ratios: list[int] = [r["OptRatio"] for r in results]

    plt.figure(figsize=(12, 7))
    baseline: list[float] = [1.0] * len(n_values)
    plt.plot(
        n_values,
        baseline,
        label="Эратосфен (базис)",
        linestyle="--",
        color="#3B82F6",
        linewidth=2,
        dashes=[5, 5],
    )
    plt.plot(
        n_values,
        atkin_ratios,
        label="Аткин",
        marker="s",
        color="#EF4444",
        linewidth=2,
    )
    plt.plot(
        n_values,
        optimized_ratios,
        label="Оптимизированный",
        marker="^",
        color="#22C55E",
        linewidth=2,
    )

    plt.title("Относительная производительность (базис: Эратосфен = 1.0)")
    plt.ylim(bottom=0)
    plt.xlabel("Число (n)")
    plt.ylabel("Относительное время")
    plt.legend(loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig("dist/" + filename)
    plt.close()
    logger.info(f"✓ График соотношения: {filename}")
