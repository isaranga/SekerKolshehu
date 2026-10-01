import json
import re
from pathlib import Path

from seker.cli import run_poll
from seker.visualization import DATA_PLACEHOLDER, OUTPUT_FILENAME, build_payload


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _extract_payload(html: str) -> dict:
    match = re.search(r"const DATA = (.*?);\n", html)
    assert match, "embedded data not found"
    return json.loads(match.group(1).replace("<\\/", "</"))


class TestVisualization:
    def test_run_poll_writes_visualization(self, tmp_path):
        output_dir = tmp_path / "output"
        run_poll(
            data_dir=DATA_DIR,
            output_dir=output_dir,
            election="25th-Knesset-2022",
            poll_name="2022-10-27-maariv",
            n_iterations=1000,
            seed=42,
        )

        path = output_dir / "25th-Knesset-2022" / "2022-10-27-maariv" / OUTPUT_FILENAME
        assert path.exists()
        html = path.read_text(encoding="utf-8")
        assert DATA_PLACEHOLDER not in html
        assert 'dir="rtl"' in html

        payload = _extract_payload(html)
        assert payload["iterations"] == 1000
        assert payload["meta"]["date"] == "2022-10-27"
        assert payload["meta"]["media"] == "מעריב"
        assert payload["meta"]["sample_size"] == 1005

        parties = payload["parties"]
        symbols = [p["symbol"] for p in parties]
        assert "מחל" in symbols
        likud = parties[symbols.index("מחל")]
        assert likud["name"] == "הליכוד"
        assert likud["poll_share"] == 0.232
        assert len(likud["counts"]) == 121
        assert sum(likud["counts"]) == 1000

        avgs = [p["avg_seats"] for p in parties]
        assert avgs == sorted(avgs, reverse=True)

    def test_rare_pass_is_active_despite_rounded_probability(self):
        stats = {
            "A": {"avg_seats": 0.0, "prob_pass_threshold": 0.0, "ci_lower": 0, "ci_upper": 0},
            "B": {"avg_seats": 0.0, "prob_pass_threshold": 0.0, "ci_lower": 0, "ci_upper": 0},
        }
        counts = {
            "A": [99_998, 0, 0, 0, 2] + [0] * 116,
            "B": [100_000] + [0] * 120,
        }
        payload = build_payload({}, {"results": {}}, stats, counts, "e", "p")
        passed = {p["symbol"]: p["passed_any"] for p in payload["parties"]}
        assert passed == {"A": True, "B": False}
