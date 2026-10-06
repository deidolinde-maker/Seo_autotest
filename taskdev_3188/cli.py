from __future__ import annotations

import argparse
import os
from pathlib import Path

from .collector import Collector, utc_now
from .allure_report import write_allure_results
from .report import save_report
from .storage import load_snapshot, read_urls, save_snapshot
from .telegram import send_report
from .validator import site_for_url, validate_page


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TASKDEV-3188 SEO monitor")
    parser.add_argument("--urls", default="urls.txt")
    parser.add_argument("--state-dir", default="state")
    parser.add_argument("--site", choices=("auto", "101", "mol", "pol"), default="auto")
    parser.add_argument("--allure-dir", default="allure-results")
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect = subparsers.add_parser("collect", help="manual current snapshot")
    collect.add_argument("--delay", type=float, default=0.0)
    validate = subparsers.add_parser("validate", help="collect current state and compare with baseline")
    validate.add_argument("--delay", type=float, default=0.0)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    state_dir = Path(args.state_dir)
    current_path = state_dir / "current_snapshot.json"
    baseline_path = state_dir / "approved_baseline.json"
    report_path = state_dir / "validation_report.json"

    if args.command == "collect":
        urls = read_urls(args.urls)
        snapshots = Collector(delay=args.delay).collect(urls)
        save_snapshot(current_path, snapshots, utc_now())
        # Collector is the only command that promotes a snapshot to baseline.
        save_snapshot(baseline_path, snapshots, utc_now())
        print(f"Collected {len(snapshots)} URL(s) into {current_path}")
        print(f"Approved baseline updated: {baseline_path}")
        return 0

    urls = read_urls(args.urls)
    baseline = load_snapshot(baseline_path)
    redirect_urls = {
        url for url, snapshot in baseline.items()
        if url in urls and snapshot.fetch_status == "failed" and snapshot.error == "redirect"
    }
    urls_to_check = [url for url in urls if url not in redirect_urls]
    snapshots = Collector(delay=args.delay).collect(urls_to_check)
    snapshots.extend(baseline[url] for url in redirect_urls if url in baseline)
    save_snapshot(current_path, snapshots, utc_now())
    current = load_snapshot(current_path)
    results = [
        validate_page(snapshot, baseline.get(url), site_for_url(url) if args.site == "auto" else args.site)
        for url, snapshot in current.items()
    ]
    report = save_report(report_path, results, utc_now())
    write_allure_results(results, args.allure_dir)
    if not send_report(report, os.getenv("BUILD_URL", "")):
        print("Telegram notification failed")
        return 2
    print(report["counters"])
    return 1 if any(report["counters"][key] for key in ("changed", "errors", "unavailable")) else 0


if __name__ == "__main__":
    raise SystemExit(main())
