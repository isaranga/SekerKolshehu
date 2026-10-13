import json

from seker.pages import ROWS_PLACEHOLDER, build_site
from seker.visualization import OUTPUT_FILENAME


def _add_poll(data_dir, output_dir, election, poll_name, date, with_viz=True):
    polls_dir = data_dir / election / "polls"
    polls_dir.mkdir(parents=True, exist_ok=True)
    poll = {"date": date, "media": "כאן 11", "pollster": "Kantar", "sample_size": 1234}
    (polls_dir / f"{poll_name}.json").write_text(json.dumps(poll), encoding="utf-8")
    poll_output = output_dir / election / poll_name
    poll_output.mkdir(parents=True)
    if with_viz:
        (poll_output / OUTPUT_FILENAME).write_text(f"<html>{poll_name}</html>", encoding="utf-8")


class TestBuildSite:
    def test_builds_index_and_poll_pages(self, tmp_path):
        data_dir, output_dir, site_dir = tmp_path / "data", tmp_path / "output", tmp_path / "site"
        _add_poll(data_dir, output_dir, "e", "2026-10-01-a", "2026-10-01")
        _add_poll(data_dir, output_dir, "e", "2026-10-05-b", "2026-10-05")
        _add_poll(data_dir, output_dir, "e", "2026-10-07-c", "2026-10-07", with_viz=False)
        _add_poll(data_dir, output_dir, "other", "2022-10-27-x", "2022-10-27")

        index_path = build_site(data_dir, output_dir, "e", site_dir)

        assert index_path == site_dir / "index.html"
        assert (site_dir / ".nojekyll").exists()
        poll_page = site_dir / "2026-10-01-a" / "index.html"
        assert poll_page.read_text(encoding="utf-8") == "<html>2026-10-01-a</html>"
        assert not (site_dir / "2026-10-07-c").exists()
        assert not (site_dir / "2022-10-27-x").exists()

        html = index_path.read_text(encoding="utf-8")
        assert ROWS_PLACEHOLDER not in html
        assert 'dir="rtl"' in html
        assert "1,234" in html
        assert "05/10/2026" in html
        assert "<title>סקר כלשהו</title>" in html
        assert html.index('href="2026-10-05-b/"') < html.index('href="2026-10-01-a/"')
        assert "2026-10-07-c" not in html

    def test_replaces_stale_site(self, tmp_path):
        data_dir, output_dir, site_dir = tmp_path / "data", tmp_path / "output", tmp_path / "site"
        _add_poll(data_dir, output_dir, "e", "2026-10-01-a", "2026-10-01")
        site_dir.mkdir()
        (site_dir / "stale.html").write_text("old", encoding="utf-8")

        build_site(data_dir, output_dir, "e", site_dir)

        assert not (site_dir / "stale.html").exists()
