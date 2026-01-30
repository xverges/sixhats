#!/usr/bin/env python3
"""List accepted Architecture Decision Records.

Scans docs/adr/ for ADR files and outputs accepted ones with their rules.
This script is deterministic - same input always produces same output.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def parse_adr(filepath: Path) -> dict | None:
    """Parse an ADR file and extract metadata."""
    content = filepath.read_text()

    # Extract title from first heading
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if not title_match:
        return None
    title = title_match.group(1).strip()

    # Extract status
    status_match = re.search(r"\*\*Status:\*\*\s*(\w+)", content)
    if not status_match:
        return None
    status = status_match.group(1).strip()

    # Extract rules section (between ## Rules and next ##)
    rules_match = re.search(
        r"## Rules\s*\n(?:<!--.*?-->\s*\n)?(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )
    rules = rules_match.group(1).strip() if rules_match else ""

    return {
        "file": filepath.name,
        "title": title,
        "status": status,
        "rules": rules,
    }


def main() -> None:
    """List all accepted ADRs."""
    # Find ADR directory relative to script location
    script_dir = Path(__file__).parent
    adr_dir = script_dir.parent / "docs" / "adr"

    if not adr_dir.exists():
        print(f"Error: ADR directory not found at {adr_dir}", file=sys.stderr)
        sys.exit(1)

    # Find all ADR files (exclude README)
    adr_files = sorted(adr_dir.glob("adr-*.md"))

    if not adr_files:
        print("No ADR files found.", file=sys.stderr)
        sys.exit(1)

    # Parse and filter for accepted ADRs
    accepted_adrs = []
    for filepath in adr_files:
        adr = parse_adr(filepath)
        if adr and adr["status"].lower() == "accepted":
            accepted_adrs.append(adr)

    # Output
    if not accepted_adrs:
        print("No accepted ADRs found.")
        return

    print(f"# Accepted ADRs ({len(accepted_adrs)} total)\n")

    for adr in accepted_adrs:
        print(f"## {adr['title']}")
        print(f"**File:** {adr['file']}")
        if adr["rules"]:
            print(f"\n### Rules\n{adr['rules']}")
        print()


if __name__ == "__main__":
    main()
