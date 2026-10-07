from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from rag_redteam.payloads import generate_payload_files
from rag_redteam.reporter import render_report
from rag_redteam.scanner import scan_endpoint


def _console() -> Console:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    return Console(legacy_windows=False)


console = _console()


def main(
    endpoint: str = typer.Option(
        ...,
        "--endpoint",
        help="Local API URL of the RAG chat endpoint. POSTs JSON {\"query\": \"...\"}.",
    ),
    target_dir: Path = typer.Option(
        ...,
        "--target-dir",
        help="Directory where malicious test files will be generated.",
        file_okay=False,
    ),
) -> None:
    """Lightweight vulnerability scanner for RAG pipelines."""
    console.print("[bold]rag-redteam[/bold] — scanning RAG prompt-injection surface\n")
    payloads = generate_payload_files(target_dir)
    console.print(f"Wrote {len(payloads)} payload files to {target_dir.resolve()}\n")
    try:
        results = scan_endpoint(endpoint, payloads)
    except RuntimeError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        raise typer.Exit(code=1) from exc
    render_report(results, console=console)


def app() -> None:
    typer.run(main)
