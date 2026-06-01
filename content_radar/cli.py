"""content-radar CLI: collect trend signal, review it, synthesize post drafts.

    python -m content_radar.cli collect                 # all sources -> today's store
    python -m content_radar.cli collect --sources hackernews arxiv
    python -m content_radar.cli show --top 25           # inspect what was collected
    python -m content_radar.cli synthesize --out ../posting-system/queue --n 5
"""
from __future__ import annotations

import argparse
import datetime as _dt

from . import config
from .collectors import REGISTRY, collect_all
from .models import Item
from .store import load_day, save_day


def _today() -> _dt.date:
    return _dt.date.today()


def cmd_collect(args) -> None:
    config.load_env()
    sources = args.sources or list(REGISTRY)
    print(f"collecting from: {', '.join(sources)} ...")
    items = collect_all(config.DEFAULT_INTERESTS, sources=sources)
    path = save_day(config.STORE_DIR, _today(), items)
    by_source: dict[str, int] = {}
    for it in items:
        by_source[it.source] = by_source.get(it.source, 0) + 1
    print(f"collected {len(items)} items: " +
          ", ".join(f"{k}={v}" for k, v in sorted(by_source.items())))
    print(f"saved -> {path}")


def cmd_show(args) -> None:
    items = load_day(config.STORE_DIR, _today())
    if not items:
        print("nothing collected today yet. run: collect")
        return
    for it in list(items)[: args.top]:
        print(f"[{it.source:10} {it.score:>5}] {it.title[:88]}")
        print(f"             {it.url}")


def cmd_synthesize(args) -> None:
    config.load_env()
    from .synthesize import synthesize, write_drafts

    key = config.anthropic_api_key()
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY not set (copy .env.example to .env).")
    items = load_day(config.STORE_DIR, _today())
    if not items:
        raise SystemExit("no collected items for today. run `collect` first.")
    print(f"synthesizing {args.n} drafts from {len(items)} items with {config.synth_model()} ...")
    drafts = synthesize(items, api_key=key, model=config.synth_model(),
                        n_drafts=args.n, item_limit=args.item_limit)
    paths = write_drafts(drafts, args.out, _today(), spacing_days=args.spacing)
    print(f"wrote {len(paths)} draft(s) to {args.out}:")
    for p in paths:
        print(f"  - {p.name}")
    print("\nreview them, then approve & post via your posting queue.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="content_radar.cli",
                                     description="Collect AI/dev trend signal and draft posts.")
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("collect", help="collect signal from sources into today's store")
    c.add_argument("--sources", nargs="*", choices=list(REGISTRY), default=None)
    c.set_defaults(func=cmd_collect)

    s = sub.add_parser("show", help="print what was collected today")
    s.add_argument("--top", type=int, default=30)
    s.set_defaults(func=cmd_show)

    y = sub.add_parser("synthesize", help="draft posts from today's signal via Claude")
    y.add_argument("--out", default="./drafts", help="output dir for draft .md files")
    y.add_argument("--n", type=int, default=5, help="number of drafts")
    y.add_argument("--item-limit", type=int, default=40, help="top items fed to the model")
    y.add_argument("--spacing", type=int, default=2, help="days between draft publish_dates")
    y.set_defaults(func=cmd_synthesize)

    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
