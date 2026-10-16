"""Seam: generator output matches the committed solution notebook."""

import json
import subprocess
import sys
from pathlib import Path

TK56 = Path(__file__).resolve().parent.parent
COMMITTED = TK56 / "Текущий контроль 3.ipynb"


def test_builder_reproduces_committed_notebook(tmp_path):
    out = tmp_path / "rebuilt.ipynb"
    r = subprocess.run(
        [sys.executable, "scripts/build_tk3_solution.py", str(out)],
        cwd=TK56,
        capture_output=True,
        text=True,
        check=True,
    )
    built = json.loads(out.read_text(encoding="utf-8"))
    ref = json.loads(COMMITTED.read_text(encoding="utf-8"))
    assert [c["cell_type"] for c in built["cells"]] == [
        c["cell_type"] for c in ref["cells"]
    ]
    for b, r_ in zip(built["cells"], ref["cells"]):
        assert "".join(b["source"]) == "".join(r_["source"])
    assert built["metadata"]["kernelspec"] == ref["metadata"]["kernelspec"]
