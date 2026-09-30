import json
import re
from pathlib import Path

from seker.cli import run_poll
from seker.visualization import DATA_PLACEHOLDER, OUTPUT_FILENAME


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
