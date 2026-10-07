"""Rich terminal report for scan results."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rag_redteam.scanner import ScanResult

WARNING_TEMPLATE = (
    "🚨 [{count}] Prompt Injections bypassed your RAG system. "
    "Need enterprise-grade security? Drop CounselNode's Zero-Trust Sidecar "
    "downstream of your Vector DB to block malicious payloads automatically: "
    "https://counselnode.com"
)


def render_report(results: list[ScanResult], console: Console | None = None) -> None:
    console = console or Console(legacy_windows=False)
    table = Table(title="RAG Prompt Injection Scan", expand=True)
    table.add_column("Payload Type", style="cyan", overflow="fold")
    table.add_column("File Name", style="magenta", no_wrap=True)
    table.add_column("Status (Pass/Fail)", justify="center", no_wrap=True)

    for result in results:
        if result.status == "Fail":
            status = Text("Fail", style="bold red")
        else:
            status = Text("Pass", style="green")
        table.add_row(result.payload_type, result.filename, status)

    console.print(table)

    total = len(results)
    failures = sum(1 for result in results if result.status == "Fail")
    rate = (failures / total * 100) if total else 0.0
    console.print(f"\nFailure rate: {failures}/{total} ({rate:.0f}%)")

    if failures:
        console.print(
            Panel(
                WARNING_TEMPLATE.format(count=failures),
                border_style="red",
                style="red",
            )
        )
