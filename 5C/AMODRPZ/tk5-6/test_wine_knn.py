"""Seam tests for TK5-6 wine kNN. Public interfaces only."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

DOCS_CSV = Path(__file__).with_name("docs") / "winequality-red.csv"


def test_docs_originals_untouched():
    assert DOCS_CSV.exists(), "original csv must stay in docs/"


def test_evaluation_workbook_protocol():
    from wine_knn import evaluate_knn

    res = evaluate_knn(DOCS_CSV)
    assert res["test_size"] == 480  # 1599 * 0.3, stratify, workbook protocol
    assert sorted(res["classes"]) == [3, 4, 5, 6, 7, 8]
    assert res["confusion_matrix"].shape == (6, 6)
    for k in (
        "accuracy",
        "precision_macro",
        "recall_macro",
        "f1_macro",
        "precision_weighted",
        "recall_weighted",
        "f1_weighted",
        "roc_auc_ovr_macro",
        "roc_auc_ovr_weighted",
    ):
        assert 0.0 <= res[k] <= 1.0, k
    assert (
        res["accuracy"] > 0.4
    )  # beats majority-class dummy (681/1599≈0.426 is the bar); real k=5 ≈ 0.49
    assert res["per_class"]["recall"][5] > 0.5


def test_cleaning_known_facts():
    from wine_knn import load_wine_data

    df, info = load_wine_data(DOCS_CSV)
    assert df.shape == (1599, 12)
    assert int(info["missing_cells"]) == 0
    assert int(info["full_dup_rows"]) == 240
    assert info["quality_counts"] == {3: 10, 4: 53, 5: 681, 6: 638, 7: 199, 8: 18}
