"""content-radar CLI: collect trend signal, review it, synthesize post drafts.

    python -m content_radar.cli collect                 # all sources -> today's store
    python -m content_radar.cli collect --sources hackernews arxiv
    python -m content_radar.cli show --top 25           # inspect what was collected
    python -m content_radar.cli synthesize --out ../posting-system/queue --n 5
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os

from . import config
from .collectors import REGISTRY, collect_all
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


def cmd_enrich(args) -> None:
    config.load_env()
    from .enrich import enrich_items
    items = list(load_day(config.STORE_DIR, _today()))
    if not items:
        raise SystemExit("nothing collected today. run `collect` first.")
    print(f"enriching up to {args.top} items (fetching full article text) ...")
    enriched = enrich_items(items, top_n=args.top)
    save_day(config.STORE_DIR, _today(), enriched)
    print("saved enriched items back to the corpus.")


def cmd_index(args) -> None:
    config.load_env()
    from . import rag
    if not rag.configured():
        raise SystemExit("set QDRANT_URL + QDRANT_API_KEY to index into Qdrant.")
    rag.ensure_datetime_index()
    if args.all:
        from .kb import load_corpus
        items = load_corpus(config.STORE_DIR)
    else:
        items = list(load_day(config.STORE_DIR, _today()))
    print(f"embedding + upserting {len(items)} items into Qdrant ...")
    n = rag.index_items(items)
    print(f"indexed {n} items into Qdrant collection '{rag.COLLECTION}'.")


def cmd_import(args) -> None:
    config.load_env()
    import json
    from pathlib import Path
    from . import rag
    from .collectors import gmail_imap

    items = gmail_imap.fetch(args.query, limit=args.limit)
    print(f"fetched {len(items)} emails matching {args.query!r}")
    if not items:
        return
    # persist to a dated, committed corpus archive (dedup by message id)
    archive = Path(config.STORE_DIR) / "raw" / "gmail-archive.json"
    archive.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(archive.read_text(encoding="utf-8")) if archive.exists() else []
    seen = {d["id"] for d in existing}
    merged = existing + [it.to_dict() for it in items if it.id not in seen]
    archive.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"corpus archive now holds {len(merged)} emails -> {archive}")
    dated = sorted((it.created for it in items if it.created))
    if dated:
        print(f"date range: {dated[0]}  ..  {dated[-1]}")
    if rag.configured():
        rag.ensure_datetime_index()
        print(f"embedding + indexing {len(items)} into Qdrant ...")
        print(f"indexed {rag.index_items(items)} into Qdrant.")
    else:
        print("Qdrant not configured — saved to corpus only.")


def cmd_eval(args) -> None:
    config.load_env()
    import json
    from pathlib import Path
    from .eval_qa import generate_questions, run
    if args.generate:
        qs = generate_questions(args.generate, config.synth_model())
        Path(args.questions).write_text(json.dumps(qs, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
        print(f"wrote {len(qs)} questions -> {args.questions}")
        return
    qs = json.loads(Path(args.questions).read_text(encoding="utf-8"))
    if args.limit:
        qs = qs[: args.limit]
    run(qs, out_path=args.out)


def cmd_check_ainews(args) -> None:
    """Light poll for the AINews watcher: is a fresh, unforwarded newsletter waiting?

    Designed for CI — writes `found=true|false` to $GITHUB_OUTPUT so the workflow
    only installs the heavy translation/indexing stack when there is real work.
    """
    config.load_env()
    from . import watch

    n = watch.pending_count(args.query or None)
    found = "true" if n > 0 else "false"
    print(f"{n} fresh unforwarded newsletter(s) -> found={found}")
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as fh:
            fh.write(f"found={found}\n")


def cmd_email_digest(args) -> None:
    config.load_env()
    from . import mailer
    from .digest import chinese_newsletter_markdown

    if not mailer.configured():
        raise SystemExit("set GMAIL_USER + GMAIL_APP_PASSWORD to send the digest email.")

    # Pull the latest AINews newsletter in FULL (no digest truncation), so the
    # Chinese edition mirrors the original's depth section-for-section.
    if args.if_new:
        # Watcher mode: only a fresh issue that has not been forwarded yet
        # (dedup via Gmail label — see content_radar.watch). Nothing new is a
        # normal outcome for a poll, so exit 0 quietly.
        from . import watch
        src = watch.find_unforwarded(args.query or None, max_chars=args.max_chars)
        if src is None:
            print("no fresh, unforwarded AINews — nothing to do.")
            return
    else:
        from .collectors import gmail_imap
        query = args.query or config.DEFAULT_AINEWS_QUERY
        items = gmail_imap.fetch(query, limit=1, max_chars=args.max_chars)
        if not items:
            raise SystemExit(f"no email matched {query!r} in the inbox.")
        src = items[0]

    body = src.text.split(": ", 1)[-1] if ": " in src.text[:80] else src.text
    print(f"translating '{src.title}' ({len(body)} chars) to Traditional Chinese "
          f"via {config.synth_model()} ...")
    zh = chinese_newsletter_markdown(body, config.synth_model())
    subject = config.forwarded_subject(src.title)
    to = mailer.send_markdown_email(subject, zh, to_addr=args.to or None)
    print(f"sent '{subject}' ({len(zh)} chars) -> {to}")

    if args.if_new:
        # Label only AFTER the send succeeded, so a failed run retries next poll.
        from . import watch
        if watch.mark_forwarded(src):
            print(f"labelled original as '{config.ainews_forwarded_label()}' (dedup marker).")
        else:
            print("WARNING: could not label the original — the next poll may resend it.")

    if args.index:
        # Same-day knowledge base: the chat bot can answer questions about this
        # issue immediately instead of waiting for tomorrow's collect+index run.
        # point_id() is deterministic, so tomorrow's run just upserts over this.
        from . import rag
        if rag.configured():
            rag.ensure_datetime_index()
            n = rag.index_items([src])
            print(f"indexed {n} chunk(s) into the knowledge base.")
        else:
            print("Qdrant not configured — skipping index.")


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
    from .synthesize import claude_cli_available, synthesize, write_drafts

    api_key = None
    if args.backend == "cli":
        if not claude_cli_available():
            raise SystemExit(
                "the `claude` CLI was not found. Install Claude Code and log in with "
                "your subscription (or in CI, set CLAUDE_CODE_OAUTH_TOKEN from "
                "`claude setup-token`). Or use --backend api with an ANTHROPIC_API_KEY."
            )
    else:  # api
        api_key = config.anthropic_api_key()
        if not api_key:
            raise SystemExit("--backend api needs ANTHROPIC_API_KEY (copy .env.example to .env).")

    items = load_day(config.STORE_DIR, _today())
    if not items:
        raise SystemExit("no collected items for today. run `collect` first.")
    print(f"synthesizing {args.n} drafts from {len(items)} items "
          f"via {args.backend} ({config.synth_model()}) ...")
    drafts = synthesize(items, model=config.synth_model(), n_drafts=args.n,
                        item_limit=args.item_limit, backend=args.backend, api_key=api_key)
    paths = write_drafts(drafts, args.out, _today(), spacing_days=args.spacing)
    print(f"wrote {len(paths)} draft(s) to {args.out}:")
    for p in paths:
        print(f"  - {p.name}")
    print("\nreview them, then approve & post via your posting queue.")


def cmd_digest(args) -> None:
    config.load_env()
    from .digest import render_digest_markdown, synthesize_digest_best_of, write_digest
    from .enrich import enrich_items
    from .synthesize import claude_cli_available

    if not claude_cli_available():
        raise SystemExit(
            "the `claude` CLI was not found. Log into Claude Code, or in CI set "
            "CLAUDE_CODE_OAUTH_TOKEN from `claude setup-token`."
        )
    items = list(load_day(config.STORE_DIR, _today()))
    if not items:
        raise SystemExit("no collected items for today. run `collect` first.")
    counts: dict[str, int] = {}
    for it in items:
        counts[it.source] = counts.get(it.source, 0) + 1

    if args.enrich > 0:
        print(f"enriching top {args.enrich} links (fetching article text) ...")
        items = enrich_items(items, top_n=args.enrich)

    print(f"building digest from {len(items)} items via {config.synth_model()} "
          f"(best-of-{args.best_of}) ...")
    data = synthesize_digest_best_of(items, model=config.synth_model(),
                                     max_themes=args.themes, item_limit=args.item_limit,
                                     n=args.best_of)
    md = render_digest_markdown(data, _today(), counts)
    path = write_digest(md, args.out, _today())
    print(f"wrote digest -> {path}  ({len(data.get('themes', []))} themes)")


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

    e = sub.add_parser("enrich", help="fetch full article text into today's corpus")
    e.add_argument("--top", type=int, default=50, help="how many items to enrich")
    e.set_defaults(func=cmd_enrich)

    ix = sub.add_parser("index", help="embed + upsert items into the Qdrant knowledge base")
    ix.add_argument("--all", action="store_true", help="backfill the whole corpus (else today)")
    ix.set_defaults(func=cmd_index)

    im = sub.add_parser("import", help="import a Gmail newsletter archive (e.g. all AINews) into the KB")
    im.add_argument("--query", default="subject:AINews", help="Gmail-syntax search")
    im.add_argument("--limit", type=int, default=1000, help="max emails to fetch")
    im.set_defaults(func=cmd_import)

    ev = sub.add_parser("eval", help="evaluate answer quality with an LLM judge")
    ev.add_argument("--generate", type=int, default=0, help="generate N questions and exit")
    ev.add_argument("--questions", default="eval_questions.json")
    ev.add_argument("--limit", type=int, default=0, help="only run the first N")
    ev.add_argument("--out", default="eval_results.json")
    ev.set_defaults(func=cmd_eval)

    y = sub.add_parser("synthesize", help="draft posts from today's signal via Claude")
    y.add_argument("--out", default="./drafts", help="output dir for draft .md files")
    y.add_argument("--n", type=int, default=5, help="number of drafts")
    y.add_argument("--item-limit", type=int, default=40, help="top items fed to the model")
    y.add_argument("--spacing", type=int, default=2, help="days between draft publish_dates")
    y.add_argument("--backend", choices=("cli", "api"), default="cli",
                   help="cli = your Claude subscription (default); api = pay-per-token key")
    y.set_defaults(func=cmd_synthesize)

    ck = sub.add_parser("check-ainews",
                        help="cheap poll: is a fresh, unforwarded AINews waiting? (for CI)")
    ck.add_argument("--query", default="",
                    help="Gmail-syntax search override (default: the dedup-aware watch query)")
    ck.set_defaults(func=cmd_check_ainews)

    me = sub.add_parser("email-digest",
                        help="email the latest AINews newsletter, fully translated to 繁中")
    me.add_argument("--query", default="",
                    help="Gmail-syntax search override (default: latest AINews; with "
                         "--if-new: the dedup-aware watch query)")
    me.add_argument("--if-new", action="store_true", dest="if_new",
                    help="watcher mode: only translate+send a fresh issue that hasn't "
                         "been forwarded yet; exit 0 quietly otherwise")
    me.add_argument("--index", action="store_true",
                    help="also index the newsletter into the Qdrant knowledge base")
    me.add_argument("--max-chars", type=int, default=60_000, dest="max_chars",
                    help="max source chars to translate (full newsletter)")
    me.add_argument("--to", default="", help="recipient (default: DIGEST_EMAIL_TO env)")
    me.set_defaults(func=cmd_email_digest)

    d = sub.add_parser("digest", help="AINews-style thematic digest of today's signal")
    d.add_argument("--out", default="./digests", help="output dir for the digest .md")
    d.add_argument("--themes", type=int, default=5, help="max number of themes")
    d.add_argument("--item-limit", type=int, default=60, help="top items fed to the model")
    d.add_argument("--enrich", type=int, default=12,
                   help="fetch+attach article text for the top N links (0 = off)")
    d.add_argument("--best-of", type=int, default=1, dest="best_of",
                   help="generate N digests and let the model pick the best (AINews-style)")
    d.set_defaults(func=cmd_digest)

    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
