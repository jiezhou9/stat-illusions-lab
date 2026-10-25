"""Capture screenshots of the running Streamlit app.

Usage:
    pip install playwright
    streamlit run app.py --server.port 8502
    python scripts/capture_screenshots.py --base-url http://127.0.0.1:8502

The script uses the locally installed Chrome, so it does not download a
Playwright browser. Screenshots are written to ``assets/screenshots``.
"""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

PAGES = ("home", "simpson", "base_rate", "multiple", "regression", "ci")
ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8502")
    parser.add_argument("--output", type=Path, default=ROOT / "assets" / "screenshots")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=1000)
    parser.add_argument("--pages", nargs="+", choices=PAGES, default=list(PAGES))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    # Some Windows sandboxes do not allow Chrome to create a profile directly
    # under %TEMP%; keep Playwright's temporary files inside the project.
    temp_dir = ROOT / ".playwright-tmp"
    temp_dir.mkdir(exist_ok=True)
    os.environ["TMP"] = str(temp_dir)
    os.environ["TEMP"] = str(temp_dir)
    tempfile.tempdir = str(temp_dir)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=1,
        )
        for key in args.pages:
            url = f"{args.base_url.rstrip('/')}/?page={key}"
            page.goto(url, wait_until="domcontentloaded")
            selector = "section.hero" if key == "home" else "header.experiment-head"
            page.wait_for_selector(selector, timeout=30_000)
            page.wait_for_timeout(2_000)
            target = args.output / f"{key}.png"
            page.screenshot(path=str(target), full_page=True)
            print(f"captured {target}")
        browser.close()


if __name__ == "__main__":
    main()
