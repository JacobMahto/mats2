#!/usr/bin/env python3
# tools/add_search_excerpts_fix.py
"""
More robust post-processor for Sphinx searchindex.js which inserts a "texts" array.
Run from project root after building HTML to docs/build/html
"""

import re
import json
from html.parser import HTMLParser
from pathlib import Path
import sys

BUILD_DIR = Path("docs/build/html")
SEARCHINDEX = BUILD_DIR / "searchindex.js"
EXCERPT_LEN = 220  # characters, adjust as needed

if not SEARCHINDEX.exists():
    print("ERROR: searchindex.js not found at:", SEARCHINDEX)
    sys.exit(1)

txt = SEARCHINDEX.read_text(encoding="utf-8", errors="ignore")

# find the start of Search.setIndex(
start = txt.find("Search.setIndex(")
if start == -1:
    print("ERROR: 'Search.setIndex(' not found in", SEARCHINDEX)
    sys.exit(1)

# find the opening brace of the JSON (first '{' after the call)
first_brace = txt.find("{", start)
if first_brace == -1:
    print("ERROR: opening '{' for JSON not found after Search.setIndex(")
    sys.exit(1)

# find the matching closing brace for the JSON by counting braces
i = first_brace
depth = 0
end_index = None
while i < len(txt):
    ch = txt[i]
    if ch == "{":
        depth += 1
    elif ch == "}":
        depth -= 1
        if depth == 0:
            end_index = i
            break
    i += 1

if end_index is None:
    print("ERROR: could not find matching closing '}' for JSON in", SEARCHINDEX)
    sys.exit(1)

json_text = txt[first_brace:end_index+1]

# parse JSON
try:
    idx = json.loads(json_text)
except json.JSONDecodeError as e:
    print("JSON decode error:", e)
    # write snippet of JSON to help debug
    snippet = json_text[:1000]
    print("JSON snippet (first 1000 chars):")
    print(snippet)
    sys.exit(1)

docnames = idx.get("docnames")
if not docnames:
    print("ERROR: 'docnames' key not found in search index JSON")
    sys.exit(1)

# helper: strip HTML tags using HTMLParser
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip = True
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip = False
    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)
    def get_text(self):
        text = " ".join(p.strip() for p in self.parts if p.strip())
        text = re.sub(r"\s+", " ", text)
        return text.strip()

texts = []
for doc in docnames:
    html_file = BUILD_DIR / f"{doc}.html"
    if not html_file.exists():
        alt = BUILD_DIR / (doc + "/index.html")
        if alt.exists():
            html_file = alt
    if not html_file.exists():
        print("WARN: html for", doc, "not found; using empty excerpt")
        texts.append("")
        continue

    extractor = TextExtractor()
    content = html_file.read_text(encoding="utf-8", errors="ignore")
    extractor.feed(content)
    body = extractor.get_text()
    excerpt = body.strip()
    if not excerpt:
        texts.append("")
        continue
    if len(excerpt) > EXCERPT_LEN:
        excerpt = excerpt[:EXCERPT_LEN].rstrip()
        excerpt += "..."
    texts.append(excerpt)

# insert or replace texts key
idx["texts"] = texts

# dump compact JSON to replace in file
new_json = json.dumps(idx, ensure_ascii=False, separators=(",", ":"))

# rebuild the new file content: everything before first_brace + new_json + everything after end_index
new_txt = txt[:first_brace] + new_json + txt[end_index+1:]

SEARCHINDEX.write_text(new_txt, encoding="utf-8")
print("Wrote updated searchindex.js with", len(texts), "excerpts.")
print("Done. Open docs/build/html/index.html and test search. If snippets are hidden, add CSS override.")
