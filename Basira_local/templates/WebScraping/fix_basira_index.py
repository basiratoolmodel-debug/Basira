from pathlib import Path


def main() -> None:
    """Apply small, safe CSS/HTML fixes to the WebScraping index template.

    The previous version of this helper contained an unterminated string literal,
    which broke Python compilation for the project. This helper is intentionally
    conservative: it only applies known textual fixes when the template exists.
    """
    index_path = Path(__file__).resolve().parent / "templates" / "index.html"
    if not index_path.exists():
        print(f"[fix_basira_index] skipped, not found: {index_path}")
        return

    text = index_path.read_text(encoding="utf-8", errors="replace")
    new = text.replace(
        ".bs-workflow-head,bs-workflow-body,bs-primary-footer{padding:18px;}",
        ".bs-workflow-head,.bs-workflow-body,.bs-primary-footer{padding:18px;}"
    )
    if new != text:
        index_path.write_text(new, encoding="utf-8")
        print(f"[fix_basira_index] updated: {index_path}")
    else:
        print(f"[fix_basira_index] no changes needed: {index_path}")


if __name__ == "__main__":
    main()
