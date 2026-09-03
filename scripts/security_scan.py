"""Small dependency-free secret scan for the local MVP."""

import re
import sys
from pathlib import Path

PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN .*PRIVATE KEY-----"),
    re.compile(
        r"(?:api[_ -]?key|password|mnemonic|seed phrase|private key)\s*[:=]\s*['\"][^'\"]+",
        re.I,
    ),
    re.compile(r"0x[a-f0-9]{64}", re.I),
]
EXCLUDED = {".git", ".venv", "__pycache__", ".pytest_cache", "tests"}


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    scanner_path = Path(__file__).resolve()
    for path in root.rglob("*"):
        if (
            not path.is_file()
            or path.resolve() == scanner_path
            or any(part in EXCLUDED for part in path.parts)
        ):
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            if any(pattern.search(line) for pattern in PATTERNS):
                findings.append(f"{path}:{line_no}")
    return findings


if __name__ == "__main__":
    findings = scan(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd())
    if findings:
        print("\n".join(findings))
        raise SystemExit(1)
    print("no credential-shaped secrets found")
