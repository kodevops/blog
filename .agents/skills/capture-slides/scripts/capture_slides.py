#!/usr/bin/env python3
"""
Download the 1st page (cover slide) image and metadata from Google Slides / Google Drive links,
auto-match them against _posts/*-struggle-<N>.markdown (title.jpg or <발표자>-발표자료.jpg),
save as .jpg in img/struggle/<N>/, and optionally update the markdown slide links.

Usage:
  python3 .agents/skills/capture-slides/scripts/capture_slides.py [img/struggle/<N>] <url1> <url2> ...
"""
import argparse
import glob
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

NAME_ALIASES = {
    "이대범": ["이대범", "daebum", "daebum-lee", "lee daebum"],
    "설영래": ["설영래", "youngrae", "seol"],
    "김태영": ["김태영", "金太永", "taeyoung", "kim taeyoung"],
    "이상준": ["이상준", "sangjun", "richellin"],
    "김범녕": ["김범녕", "bumnyeong", "kimjoin2"],
    "장은수": ["장은수", "eunsu", "unsu"],
    "정우현": ["정우현", "woohyeon"],
    "문재성": ["문재성", "jaesung"],
    "이웅희": ["이웅희", "woonghee"],
    "조유신": ["조유신", "yushin"],
    "조한규": ["조한규", "hankyu"],
    "윤준영": ["윤준영", "joonyoung"],
    "김형철": ["김형철", "hyungcheol", "yoda"],
}


def detect_struggle_num_and_dir(target_arg: str | None) -> tuple[str | None, Path]:
    if target_arg:
        if target_arg.isdigit():
            return target_arg, Path("img/struggle") / target_arg
        clean = target_arg.lstrip("/") if target_arg.startswith("/img/") else target_arg
        p = Path(clean)
        m = re.search(r"img/struggle/(\d+)", str(p))
        return (m.group(1) if m else None), p

    # Auto-detect from git branch (e.g. feature/struggle-70)
    try:
        branch = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True)
            .strip()
        )
        m = re.search(r"struggle-(\d+)", branch)
        if m:
            num = m.group(1)
            return num, Path("img/struggle") / num
    except Exception:
        pass

    # Fallback: latest _posts/*-struggle-*.markdown
    posts = sorted(glob.glob("_posts/*-struggle-*.markdown"))
    if posts:
        m = re.search(r"struggle-(\d+)\.markdown$", posts[-1])
        if m:
            num = m.group(1)
            return num, Path("img/struggle") / num

    raise SystemExit("Could not auto-detect struggle number. Please specify e.g. img/struggle/70")


def extract_file_id(url: str) -> str | None:
    m = re.search(r"/d/([a-zA-Z0-9_-]{20,})", url)
    if m:
        return m.group(1)
    m = re.search(r"[?&]id=([a-zA-Z0-9_-]{20,})", url)
    if m:
        return m.group(1)
    return None


def http_get(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "ko-KR,ko;q=0.9,ja-JP;q=0.8,en-US;q=0.7",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        content_type = resp.headers.get("Content-Type", "")
        return resp.read(), content_type


def fetch_slide_metadata_and_image(url: str, file_id: str) -> dict:
    info = {
        "url": url,
        "file_id": file_id,
        "title": "",
        "description": "",
        "og_image": "",
        "text_snippets": "",
        "image_bytes": None,
    }

    # 1. Fetch HTML page to get og:title, og:description, og:image, and embedded slide text
    try:
        raw_html, _ = http_get(url)
        body = raw_html.decode("utf-8", errors="replace")

        og_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', body)
        if og_title:
            info["title"] = html.unescape(og_title.group(1))
        else:
            title_tag = re.search(r"<title>([^<]*)</title>", body)
            if title_tag:
                info["title"] = html.unescape(title_tag.group(1))

        # If docs.google.com returned a generic loading shell (common for rtpof=true PPTX files),
        # query drive.google.com/file/d/<id>/view to get the actual filename in og:title
        if not info["title"] or "로드 중" in info["title"] or "Loading" in info["title"]:
            try:
                drive_html, _ = http_get(f"https://drive.google.com/file/d/{file_id}/view")
                drive_body = drive_html.decode("utf-8", errors="replace")
                d_title = re.search(
                    r'<meta\s+property="og:title"\s+content="([^"]*)"', drive_body
                )
                if d_title:
                    info["title"] = html.unescape(d_title.group(1))
            except Exception:
                pass

        og_desc = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', body)
        if og_desc:
            info["description"] = html.unescape(og_desc.group(1))

        og_img = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', body)
        if og_img:
            info["og_image"] = html.unescape(og_img.group(1))

        # Extract any Korean/Japanese/English text snippets embedded in DOCS_modelChunk
        korean_matches = re.findall(r"[가-힣A-Za-z0-9\s]{4,40}", body)
        # Keep only strings containing Hangul
        hangul_snippets = [s.strip() for s in korean_matches if re.search(r"[가-힣]{2,}", s)]
        info["text_snippets"] = " | ".join(dict.fromkeys(hangul_snippets[:30]))
    except Exception as exc:
        print(f"  [Warn] HTML fetch warning for {file_id}: {exc}")

    # 2. Try downloading high-res 1st page image
    candidate_urls = [
        f"https://docs.google.com/presentation/d/{file_id}/export/jpeg",
        f"https://docs.google.com/presentation/d/{file_id}/export/png",
        f"https://drive.google.com/thumbnail?id={file_id}&sz=w1920",
    ]
    if info["og_image"]:
        # Upgrade og:image resolution parameter to w1920
        hi_og = re.sub(r"=w\d+-h\d+[^&\"']*", "=w1920", info["og_image"])
        candidate_urls.append(hi_og)
        candidate_urls.append(info["og_image"])

    for cand in candidate_urls:
        try:
            data, ctype = http_get(cand)
            if data and ("image/" in ctype.lower() or data[:4] in (b"\xff\xd8\xff\xe0", b"\xff\xd8\xff\xe1", b"\x89PNG")):
                info["image_bytes"] = data
                break
        except Exception:
            continue

    return info


def save_bytes_as_jpg(image_bytes: bytes, dest_path: Path) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    # If already JPEG, write directly; if PNG/other, convert to JPEG via macOS sips
    if image_bytes[:2] == b"\xff\xd8":
        dest_path.write_bytes(image_bytes)
    else:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = Path(tmp.name)
        try:
            subprocess.run(
                ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "90", str(tmp_path), "--out", str(dest_path)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


def parse_speakers_from_post(struggle_num: str) -> tuple[Path | None, list[dict]]:
    posts = sorted(glob.glob(f"_posts/*-struggle-{struggle_num}.markdown"))
    if not posts:
        return None, []
    post_path = Path(posts[-1])
    content = post_path.read_text(encoding="utf-8")
    speakers = []
    for m in re.finditer(r"^\*\*(\d+)\.\s*([^:]+):\s*(.+?)\*\*\s*-\s*(.+?)\s*$", content, re.M):
        speakers.append(
            {
                "index": int(m.group(1)),
                "name": unicodedata.normalize("NFC", m.group(2).strip()),
                "topic": unicodedata.normalize("NFC", m.group(3).strip()),
                "current_link": m.group(4).strip(),
                "full_line": m.group(0),
            }
        )
    return post_path, speakers


def score_match(slide_info: dict, speaker: dict) -> int:
    haystack = unicodedata.normalize(
        "NFC",
        f"{slide_info['title']} {slide_info['description']} {slide_info['text_snippets']}".lower(),
    )
    score = 0
    spk_name = speaker["name"]
    aliases = NAME_ALIASES.get(spk_name, [spk_name])
    for alias in aliases:
        if alias.lower() in haystack:
            score += 50

    # Check topic words (2+ chars)
    words = re.findall(r"[가-힣A-Za-z0-9]{2,}", speaker["topic"].lower())
    stopwords = {"있는", "대한", "위해", "전에", "할", "것", "소감", "강의", "여러분의"}
    for w in words:
        if w not in stopwords and w in haystack:
            score += 20
    return score


def is_title_slide(slide_info: dict, struggle_num: str | None) -> bool:
    t = unicodedata.normalize("NFC", f"{slide_info['title']} {slide_info['description']}").lower()
    if struggle_num and (f"{struggle_num}차" in t or f"{struggle_num}次" in t):
        if any(k in t for k in ["고군분투기", "孤軍奮闘記", "title", "오프닝", "안내"]):
            return True
    if re.fullmatch(r"(제?\s*\d+\s*차\s*고군분투기|第?\s*\d+\s*次\s*孤軍奮闘記|title\.?.*)", t.strip()):
        return True
    return False


def update_post_links(post_path: Path, matched_links: dict[str, str]) -> None:
    content = post_path.read_text(encoding="utf-8")
    updated = False
    for spk_name, url in matched_links.items():
        # Encode parentheses in URL if any
        safe_url = url.replace("(", "%28").replace(")", "%29")
        pattern = rf"^(\*\*\d+\.\s*{re.escape(spk_name)}:\s*.+?\*\*\s*-\s*)(?:자료\s*\([^)]*\)|\[자료\]\([^)]*\))(\s*)$"
        new_content, count = re.subn(
            pattern,
            rf"\1[자료]({safe_url})\2",
            content,
            flags=re.M,
        )
        if count > 0 and new_content != content:
            content = new_content
            updated = True
            print(f"  [Markdown] Updated slide link for {spk_name} in {post_path}")

    if updated:
        post_path.write_text(content, encoding="utf-8")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Usage: capture_slides.py [img/struggle/<N>] <url1> [url2 ...]", file=sys.stderr)
        sys.exit(1)

    target_arg = None
    urls = []
    for a in args:
        if a.startswith("http://") or a.startswith("https://"):
            urls.append(a.strip())
        elif target_arg is None:
            target_arg = a.strip()

    struggle_num, target_dir = detect_struggle_num_and_dir(target_arg)
    target_dir.mkdir(parents=True, exist_ok=True)

    post_path, speakers = (None, [])
    if struggle_num:
        post_path, speakers = parse_speakers_from_post(struggle_num)

    print(f"Target directory: {target_dir} (Struggle #{struggle_num or 'Unknown'})")
    if post_path:
        print(f"Found post: {post_path} with speakers: {[s['name'] for s in speakers]}")

    slides = []
    for idx, url in enumerate(urls, 1):
        fid = extract_file_id(url)
        if not fid:
            print(f"[Error] Could not extract Google file ID from URL: {url}")
            continue
        print(f"\n[{idx}/{len(urls)}] Fetching {url} (id={fid}) ...")
        info = fetch_slide_metadata_and_image(url, fid)
        print(f"  Title metadata : {info['title']!r}")
        if info["description"]:
            print(f"  Desc metadata  : {info['description'][:100]!r}")
        if info["text_snippets"]:
            print(f"  Text snippets  : {info['text_snippets'][:120]!r}")
        slides.append(info)

    used_speakers = set()
    matched_links: dict[str, str] = {}

    for idx, slide in enumerate(slides, 1):
        if not slide["image_bytes"]:
            print(f"  [Error] Could not download 1st-page image for {slide['url']}")
            continue

        # 1. Check if it's the event title slide
        if is_title_slide(slide, struggle_num) and not any(
            score_match(slide, s) >= 40 for s in speakers
        ):
            out_path = target_dir / "title.jpg"
            save_bytes_as_jpg(slide["image_bytes"], out_path)
            print(f"  -> Saved as {out_path} (Matched: Event Title Slide)")
            continue

        # 2. Score against speakers
        best_spk = None
        best_score = 0
        for s in speakers:
            if s["name"] in used_speakers:
                continue
            sc = score_match(slide, s)
            if sc > best_score:
                best_score = sc
                best_spk = s

        if best_spk and best_score >= 20:
            spk_name = best_spk["name"]
            used_speakers.add(spk_name)
            matched_links[spk_name] = slide["url"]
            out_path = target_dir / f"{spk_name}-발표자료.jpg"
            save_bytes_as_jpg(slide["image_bytes"], out_path)
            print(f"  -> Saved as {out_path} (Matched speaker: {spk_name}, score={best_score})")
        else:
            # Save with candidate name so the agent can visually inspect the image to identify the speaker
            temp_out = target_dir / f"unmatched-{idx}.jpg"
            save_bytes_as_jpg(slide["image_bytes"], temp_out)
            print(
                f"  -> Saved as {temp_out} (Metadata ambiguous; inspect image to rename to title.jpg or <발표자>-발표자료.jpg)"
            )

    if post_path and matched_links:
        update_post_links(post_path, matched_links)


if __name__ == "__main__":
    main()
