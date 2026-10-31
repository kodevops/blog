#!/usr/bin/env python3
"""
Fetch a public Google Form (viewform) and extract its title and description text.
Usage:
  python3 .agents/skills/struggle-draft/scripts/fetch_form.py "<google_form_url>"
"""
import html
import json
import re
import sys
import urllib.request


def fetch_google_form(url: str) -> None:
    url = url.strip().rstrip(")")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ko-KR,ko;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8", errors="replace")

    og_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', body)
    og_desc = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', body)

    print("=== Meta Tags ===")
    if og_title:
        print("Title:", html.unescape(og_title.group(1)))
    if og_desc:
        print("Description:\n" + html.unescape(og_desc.group(1)))

    match = re.search(r"var\s+FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.*?\]);\s*</script>", body, re.S)
    if match:
        try:
            data = json.loads(match.group(1))
            print("\n=== Form Load Data ===")
            if len(data) > 1 and isinstance(data[1], list):
                form_info = data[1]
                if len(form_info) > 8 and form_info[8]:
                    print("Form Title:", form_info[8])
                if len(form_info) > 0 and form_info[0]:
                    print("Form Description:\n" + str(form_info[0]))
        except Exception as exc:
            print(f"Note: Could not parse FB_PUBLIC_LOAD_DATA_ JSON: {exc}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fetch_form.py <google_form_url>", file=sys.stderr)
        sys.exit(1)
    fetch_google_form(sys.argv[1])

