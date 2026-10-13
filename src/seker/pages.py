import shutil
from datetime import date
from html import escape
from importlib.resources import files
from pathlib import Path

from seker.io import load_poll
from seker.visualization import OUTPUT_FILENAME

ROWS_PLACEHOLDER = "<!--__ROWS__-->"
INDEX_TEMPLATE = "index.html"


def _format_date(value: str | None, fallback: str) -> str:
    try:
        return date.fromisoformat(value).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return value or fallback


def _render_row(poll_name: str, poll: dict) -> str:
    href = f"{escape(poll_name)}/"
    sample_size = poll.get("sample_size")
    date_text = escape(_format_date(poll.get("date"), poll_name))
    media = escape(str(poll.get("media") or ""))
    pollster = escape(str(poll.get("pollster") or ""))
    sample = f"{sample_size:,}" if isinstance(sample_size, int) else ""
    # Each cell links to the poll so the whole row is clickable; only the date link is focusable
    extra = f'<a href="{href}" tabindex="-1">'
    return (
        f'        <tr><td><a href="{href}">{date_text}</a></td>'
        f"<td>{extra}{media}</a></td><td>{extra}{pollster}</a></td>"
        f'<td class="num">{extra}{sample}</a></td></tr>'
    )


def render_index(polls: list[tuple[str, dict]]) -> str:
    template = (files("seker") / "templates" / INDEX_TEMPLATE).read_text(encoding="utf-8")
    rows = "\n".join(_render_row(name, poll) for name, poll in polls)
    return template.replace(ROWS_PLACEHOLDER, rows)


def build_site(data_dir: Path, output_dir: Path, election: str, site_dir: Path) -> Path:
    """Build a static site of one election's poll visualizations, newest poll first."""
    if site_dir.exists():
        shutil.rmtree(site_dir)
    site_dir.mkdir(parents=True)

    polls = []
    for poll_dir in sorted((output_dir / election).iterdir()):
        visualization = poll_dir / OUTPUT_FILENAME
        if not visualization.exists():
            continue
        poll = load_poll(data_dir / election / "polls" / f"{poll_dir.name}.json")
        (site_dir / poll_dir.name).mkdir()
        shutil.copyfile(visualization, site_dir / poll_dir.name / "index.html")
        polls.append((poll_dir.name, poll))

    polls.sort(key=lambda p: (p[1].get("date") or "", p[0]), reverse=True)
    index_path = site_dir / "index.html"
    index_path.write_text(render_index(polls), encoding="utf-8")
    (site_dir / ".nojekyll").touch()
    return index_path
