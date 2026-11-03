#!/usr/bin/env python3
"""Kiro IDE の公式 changelog ページから本文構造を機械抽出する。

kiro.dev は Next.js（App Router）で構築されており、ページ本文は HTML の可視部分では
なく RSC（React Server Components）ペイロードとして `self.__next_f.push(...)` の
連なりに埋め込まれている。本スクリプトはそれを復元して、系列タイトル・日付・版番号・
機能セクション・Improvements/Fixes・**各パッチの本体**を構造化して取り出す。

使い方:
    # 取得（末尾スラッシュ必須・User-Agent 必須）
    curl -sSL -A "Mozilla/5.0" -o 1-0.html "https://kiro.dev/changelog/ide/1-0/"

    # 抽出
    python3 extract-changelog.py 1-0.html            # JSON
    python3 extract-changelog.py --text 1-0.html     # 人が読む形
    python3 extract-changelog.py --items 1-4-51.html # 項目（ID・題・リンク）を1行ずつ

重要な前提（`.github/UPDATE_GUIDE.md` §3・§5 と対応）:

- ページ左の「Latest Patches」ブロックにある `"patches":[{id,version,date}]` は
  **ナビゲーションの索引**であり、version と date しか持たない。
  **パッチの説明文は本文側の別ノード `<div id="patch-X-Y-Z">` に存在する。**
  索引に説明が無いことを「説明が存在しない」と読み替えてはならない。
- 網羅性（全パッチの列挙）は索引で担保し、記述内容は本文ノードで判断する。

項目（`entries`・`items()`・`releases()`）:

- `extract()` の `entries` は、`li` と `p`（`<p><strong>ラベル</strong></p>` だけの段落を除く）を
  出現順に持つ。各要素は `kind`・`patch`・`section`・`title`・`text`・`links`・`terms`・`in_details`。
  既存のキー（`sections`・`patches` など）の作り方は変えていない。
- 項目の区切りは `items()` が決める。`<strong>` を区切りとみなさない（1.4.51 では `<strong>` が
  29 個あり、項目は 14）。題は「最初の子が `<strong>` で、末尾が `:`」のときだけ取る。
- 1つの版の項目は `releases()` が専用ページ → 系列ランディング本文 → 系列ページ内パッチの順に選ぶ
  （`pick_release()`）。専用ページを持つ版は、系列ページ側のパッチが1行の案内しか持たないため。
"""
import argparse
import collections
import json
import os
import re
import sys

# 月名テーブルを自前で持つ（`%b` はロケール依存のため使わない）
MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10,
    "November": 11, "December": 12,
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def to_iso(date_str):
    """`Jul 28, 2026` / `July 28, 2026` を `2026-07-28` にする。

    タイムゾーン変換は行わない（公式ページの表示日をそのまま日付として扱う）。
    """
    if not date_str:
        return None
    m = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$', date_str.strip())
    if not m or m.group(1) not in MONTHS:
        return None
    return f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"


def flight(html):
    """`self.__next_f.push([1,"..."])` の断片を連結して RSC フライトを復元する。

    1断片では JSON が閉じないので、必ず全断片を連結してから行分割する。
    """
    parts = []
    for m in re.finditer(r'self\.__next_f\.push\(\[1,\s*("(?:[^"\\]|\\.)*")\s*\]\)', html):
        parts.append(json.loads(m.group(1)))
    return "".join(parts)


def rowtable(fl):
    """フライトを 行ID -> JSON値 の辞書にする。

    `I[` はクライアントモジュール参照、`HL[` はプリロード、`T` はテキストストリームで
    いずれも本文ではないため除外する。
    """
    table = {}
    for line in fl.split("\n"):
        m = re.match(r'^([0-9a-f]+):(.*)$', line)
        if not m or m.group(2).startswith(("I[", "HL[", "T")):
            continue
        try:
            table[m.group(1)] = json.loads(m.group(2))
        except json.JSONDecodeError:
            pass
    return table


def roots(table):
    """他の行から `$L<id>` で参照されていない行 = ルートツリー。

    全行を起点に走査すると、`$L` で遅延参照される行（li 単体の行など）を
    ルート経由と単体で二重に拾ってしまうため、ルートのみを起点にする。
    """
    referenced = set()
    for v in table.values():
        for m in re.finditer(r'"\$L([0-9a-f]+)"', json.dumps(v)):
            referenced.add(m.group(1))
    return [r for r in sorted(table, key=lambda x: int(x, 16)) if r not in referenced]


def text_of(node, table):
    """ノード配下のテキストを連結する。"""
    if node is None or not isinstance(node, (str, list, dict)):
        return ""
    if isinstance(node, str):
        if node.startswith("$L"):
            return text_of(table.get(node[2:]), table)
        return "" if node.startswith("$") else node
    if isinstance(node, dict):
        return text_of(node.get("children"), table)
    if len(node) == 4 and node[0] == "$" and isinstance(node[1], str):
        props = node[3] if isinstance(node[3], dict) else {}
        return text_of(props.get("children"), table)
    return "".join(text_of(x, table) for x in node)


def links_of(node, table, out=None):
    """ノード配下の要素の `href` プロップを出現順に集める。

    リンクは `a` 要素ではなく、クライアント部品（Next.js の Link。タグが `$L<id>`）の
    `href` に入る。`$` で始まる値（`$undefined`）は捨てる。
    """
    if out is None:
        out = []
    if isinstance(node, str):
        if node.startswith("$L"):
            links_of(table.get(node[2:]), table, out)
        return out
    if isinstance(node, dict):
        links_of(node.get("children"), table, out)
        return out
    if isinstance(node, list):
        if len(node) == 4 and node[0] == "$" and isinstance(node[1], str):
            props = node[3] if isinstance(node[3], dict) else {}
            h = props.get("href")
            if isinstance(h, str) and not h.startswith("$"):
                out.append({"href": h, "text": clean(text_of(props.get("children"), table))})
            links_of(props.get("children"), table, out)
            return out
        for x in node:
            links_of(x, table, out)
    return out


def lead_title(node, table):
    """`li`/`p` の最初の子が `<strong>…:</strong>` なら、その文字列（末尾のコロンを除く）。"""
    kids = node
    if isinstance(kids, str) and kids.startswith("$L"):
        kids = table.get(kids[2:])
    if isinstance(kids, list) and len(kids) == 4 and kids[0] == "$":
        kids = [kids]
    if not isinstance(kids, list) or not kids:
        return None
    first = kids[0]
    if isinstance(first, str) and first.startswith("$L"):
        first = table.get(first[2:])
    if isinstance(first, list) and len(first) == 4 and first[0] == "$" and first[1] == "strong":
        props = first[3] if isinstance(first[3], dict) else {}
        t = clean(text_of(props.get("children"), table))
        if t.endswith(":"):
            return t[:-1].strip()
    return None


def terms_of(node, table, out=None, inlink=False):
    """項目内の `<strong>`・`<code>` の文字列を出現順・重複なしで集める。

    先頭の題（末尾が `:`）とリンクの中（「Learn more ->」）は除く。
    """
    if out is None:
        out = []
    if isinstance(node, str):
        if node.startswith("$L"):
            terms_of(table.get(node[2:]), table, out, inlink)
        return out
    if isinstance(node, dict):
        terms_of(node.get("children"), table, out, inlink)
        return out
    if isinstance(node, list):
        if len(node) == 4 and node[0] == "$" and isinstance(node[1], str):
            props = node[3] if isinstance(node[3], dict) else {}
            if node[1] in ("strong", "code") and not inlink:
                t = clean(text_of(props.get("children"), table))
                if t and not t.endswith(":") and t not in out:
                    out.append(t)
                return out
            terms_of(props.get("children"), table, out, inlink or "href" in props)
            return out
        for x in node:
            terms_of(x, table, out, inlink)
    return out


def entry(kind, kids, text, acc, table):
    """`entries` の1要素。`section` は、その時点のコンテナ（ページ本文か1パッチ）の最後の節の題。"""
    target = acc["cur_patch"] or acc
    return {
        "kind": kind,
        "patch": acc["cur_patch"]["version"] if acc["cur_patch"] else None,
        "section": target["sections"][-1]["title"] if target["sections"] else None,
        "title": lead_title(kids, table),
        "text": text,
        "links": links_of(kids, table),
        "terms": terms_of(kids, table),
        "in_details": bool(acc["in_details"]),
    }


def clean(s):
    return re.sub(r'\s+', ' ', s).replace(" Learn more ->", "").strip()


def new_section(title):
    return {"title": title, "items": [], "groups": []}


def walk(node, table, acc):
    """見出し・アコーディオン・箇条書き・段落・パッチ本体を出現順に収集する。"""
    if node is None or isinstance(node, (int, float, bool)):
        return
    if isinstance(node, str):
        if node.startswith("$L"):
            walk(table.get(node[2:]), table, acc)
        return
    if isinstance(node, dict):
        # 要素の props ではない素の dict（フライトのルート等）は全値をたどる
        if "children" in node:
            walk(node["children"], table, acc)
        else:
            for v in node.values():
                walk(v, table, acc)
        return
    if len(node) == 4 and node[0] == "$" and isinstance(node[1], str):
        tag = node[1]
        props = node[3] if isinstance(node[3], dict) else {}
        target = acc["cur_patch"] if acc["cur_patch"] else acc

        # アコーディオン見出し（Improvements / Fixes / New Features / Patches ...）。
        # 動画・図の埋め込みも `title` プロップを持つが、値は `$undefined` か
        # children を持たないので、children を伴うものだけを見出しとして扱う。
        if isinstance(props.get("title"), str) and not props["title"].startswith("$") \
                and props.get("children") is not None:
            target["sections"].append(new_section(props["title"]))
            walk(props.get("children"), table, acc)
            return

        # Patches セクション内の <div id="patch-X-Y-Z"> は1パッチの境界。
        # 配下に version|date の見出し段落＋説明段落を持ち、パッチによっては
        # さらに独自の Improvements / Bug Fixes 見出しと箇条書きを持つ。
        if isinstance(props.get("id"), str) and props["id"].startswith("patch-"):
            patch = {
                "version": props["id"][len("patch-"):].replace("-", "."),
                "date": None, "date_iso": None, "lines": [], "sections": [],
            }
            acc["patches"].append(patch)
            prev, acc["cur_patch"] = acc["cur_patch"], patch
            walk(props.get("children"), table, acc)
            acc["cur_patch"] = prev
            return

        if tag == "h1":
            acc.setdefault("title", clean(text_of(props.get("children"), table)))
            return

        if tag in ("h2", "h3", "h4"):
            t = clean(text_of(props.get("children"), table))
            if t:
                target["sections"].append(new_section(t))
            return

        # <details> の中は動画のトランスクリプト。entries に印を付ける（R0。items() が捨てる）
        if tag == "details":
            acc["in_details"] += 1
            walk(props.get("children"), table, acc)
            acc["in_details"] -= 1
            return

        if tag == "li":
            t = clean(text_of(props.get("children"), table))
            if t:
                acc["entries"].append(entry("li", props.get("children"), t, acc, table))
                if not target["sections"]:
                    target["sections"].append(new_section(None))
                sec = target["sections"][-1]
                (sec["groups"][-1]["items"] if sec["groups"] else sec["items"]).append(t)
            return

        if tag == "p":
            t = clean(text_of(props.get("children"), table))
            if not t:
                return
            # <p><strong>ラベル</strong></p> だけの段落は箇条書きのグループ見出し
            kids = props.get("children")
            only_strong = (
                isinstance(kids, list) and len(kids) == 4
                and kids[0] == "$" and kids[1] == "strong"
            )
            if not only_strong:
                acc["entries"].append(entry("p", kids, t, acc, table))
            cur = acc["cur_patch"]
            if cur is not None:
                # パッチ見出し: <p><strong>0.8.206</strong><span> | Jan 28, 2026</span></p>
                m = re.match(r'^(\d+\.\d+\.\d+)\s*\|\s*(.+)$', t)
                if m:
                    cur["date"] = m.group(2).strip()
                    cur["date_iso"] = to_iso(cur["date"])
                elif cur["sections"]:
                    sec = cur["sections"][-1]
                    if only_strong:
                        sec["groups"].append({"label": t, "items": []})
                    else:
                        (sec["groups"][-1]["items"] if sec["groups"] else sec["items"]).append(t)
                else:
                    cur["lines"].append(t)
                return
            if not acc["sections"]:
                acc["intro"].append(t)
            elif only_strong:
                acc["sections"][-1]["groups"].append({"label": t, "items": []})
            else:
                acc["sections"][-1]["items"].append(t)
            return

        walk(props.get("children"), table, acc)
        return

    for x in node:
        walk(x, table, acc)


def patch_index(html):
    """「Latest Patches」の索引 JSON を返す（網羅性の担保用）。"""
    s = html.replace('\\"', '"')
    m = re.search(r'"patches":(\[.*?\])', s)
    if not m:
        return None      # 呼び出し側で「構造変化」として扱う
    return json.loads(m.group(1))


def extract(path):
    html = open(path, encoding="utf-8").read()
    table = rowtable(flight(html))
    acc = {"intro": [], "sections": [], "patches": [], "cur_patch": None,
           "entries": [], "in_details": 0}
    for rid in roots(table):
        walk(table[rid], table, acc)

    # 日付・版番号は素の HTML から拾う（RSC 側では装飾ノードに埋もれる）。
    # 系列ページは冒頭の「Latest Patches」ブロックにも版番号と日付が並ぶため、
    # 先頭マッチだと最新パッチの値を拾ってしまう（0.3 系でランディングの
    # Sep 29 ではなくパッチ 0.3.9 の Oct 2 を取る）。本文の値は h1 の直前に
    # あるので、h1 より前の「最後の」マッチを採る。
    title = acc.get("title") or ""
    head = html[:html.find(title)] if title and title in html else html
    vers = re.findall(r'>(\d+\.\d+(?:\.\d+)?)</', head) or \
        re.findall(r'>(\d+\.\d+(?:\.\d+)?)</', html)
    dates = re.findall(r'>([A-Z][a-z]+ \d{1,2}, \d{4})<', head) or \
        re.findall(r'>([A-Z][a-z]+ \d{1,2}, \d{4})<', html)
    date = dates[-1] if dates else None

    # PREVIOUS / NEXT ナビの見出しは本文ではないので、中身のない重複を落とす
    secs, seen = [], set()
    for s in acc["sections"]:
        if s["title"] in seen and not (s["items"] or s["groups"]):
            continue
        seen.add(s["title"])
        secs.append(s)

    index = patch_index(html)
    result = {
        "file": path,
        "version": vers[-1] if vers else None,
        "date": date,
        "date_iso": to_iso(date),
        "title": acc.get("title"),
        "intro": acc["intro"],
        "sections": [s for s in secs if s["items"] or s["groups"]],
        "patches": acc["patches"],
        "patch_index_count": len(index) if index is not None else None,
        "entries": acc["entries"],
    }
    # 索引と本文のパッチ数が食い違ったら構造変化の可能性がある
    if index is not None and len(index) != len(acc["patches"]):
        result["warning"] = (
            f"索引 {len(index)} 件に対し本文ノード {len(acc['patches'])} 件"
            "（ページ構造が変わった可能性あり）"
        )
    return result


PATCH_HEADING_RE = re.compile(r'^\d+\.\d+\.\d+\s*\|')
SERIES_SLUG_RE = re.compile(r'^\d+-\d+$')


def items(entries):
    """1コンテナ（ページ本文か1パッチ）の entries から項目の配列を作る（設計の規則 R0〜R7）。

    - R0 `<details>` の中は捨てる。R1 パッチの見出し段落（`X.Y.Z | 日付`）は捨てる
    - R2 見出しの無い段落は概要。ほかに項目が無いときだけ概要を1項目にする
    - R3 段落を1つ以上含む節は、節全体を1項目にする（題＝節の見出し）
    - R4・R5 `li` だけの節と節に属さない `li` は、`li` 1つを1項目にする
    - R7 題は `lead_title()`（最初の子の `<strong>` の末尾が `:` のときだけ）
    """
    es = [e for e in entries
          if not e["in_details"] and not (e["kind"] == "p" and PATCH_HEADING_RE.match(e["text"]))]
    intro = [e for e in es if e["section"] is None and e["kind"] == "p"]
    rest = [e for e in es if not (e["section"] is None and e["kind"] == "p")]
    by_section = collections.OrderedDict()
    for e in rest:
        by_section.setdefault(e["section"], []).append(e)
    out = []
    for sec, group in by_section.items():
        if sec is not None and any(e["kind"] == "p" for e in group):
            out.append({
                "section": sec, "title": sec, "unit": "section",
                "body": " ".join(e["text"] for e in group),
                "links": [l for e in group for l in e["links"]],
                "terms": [t for e in group for t in e["terms"]],
            })
            continue
        for e in group:
            body = e["text"]
            if e["title"] and body.startswith(e["title"] + ":"):
                body = body[len(e["title"]) + 1:].strip()
            out.append({
                "section": sec, "title": e["title"], "unit": "li",
                "body": body, "links": e["links"], "terms": e["terms"],
            })
    if not out and intro:
        out.append({
            "section": None, "title": None, "unit": "intro",
            "body": " ".join(e["text"] for e in intro),
            "links": [l for e in intro for l in e["links"]],
            "terms": [t for e in intro for t in e["terms"]],
        })
    return out


def releases(paths, pages=None):
    """全ページから {版: [候補コンテナ]} を作る。

    候補は {"kind": dedicated|series|patch, "slug", "version", "date_iso", "items"}。
    kind は、専用ページの本文（dedicated）、系列ランディングの本文（series）、
    系列ページ内の1パッチ（patch）。`pages` に extract() の結果（paths と同じ順）を渡すと再抽出しない。
    """
    out = {}
    for n, path in enumerate(paths):
        d = pages[n] if pages is not None else extract(path)
        slug = os.path.basename(path)[:-len(".html")] if path.endswith(".html") else os.path.basename(path)
        series = bool(SERIES_SLUG_RE.match(slug))
        body = [e for e in d["entries"] if e["patch"] is None]
        if d["version"]:
            out.setdefault(d["version"], []).append({
                "kind": "series" if series else "dedicated", "slug": slug,
                "version": d["version"], "date_iso": d["date_iso"], "items": items(body),
            })
        if series:
            by_patch = collections.OrderedDict()
            for e in d["entries"]:
                if e["patch"]:
                    by_patch.setdefault(e["patch"], []).append(e)
            dates = {p["version"]: p["date_iso"] for p in d["patches"]}
            for v, es in by_patch.items():
                out.setdefault(v, []).append({
                    "kind": "patch", "slug": slug, "version": v,
                    "date_iso": dates.get(v), "items": items(es),
                })
    return out


def pick_release(cands):
    """R8: 専用ページ → 系列ランディング本文 → 系列ページ内パッチの順に1つ選ぶ。"""
    for kind in ("dedicated", "series", "patch"):
        for c in cands:
            if c["kind"] == kind:
                return c
    return None


def version_key(v):
    return [int(x) for x in v.split(".")]


def render_items(rel):
    """--items の出力。版の降順に `ID<TAB>題（無ければ本文の先頭60字）<TAB>リンク` を1行ずつ。"""
    out = []
    for v in sorted(rel, key=version_key, reverse=True):
        c = pick_release(rel[v])
        out.append(f"[{v}] {c['date_iso']} | {c['kind']}:{c['slug']}")
        for n, it in enumerate(c["items"], 1):
            title = it["title"] or (it["body"][:60] + ("…" if len(it["body"]) > 60 else ""))
            links = " ".join(l["href"] for l in it["links"]) or "-"
            out.append(f"{item_id(v, n, len(c['items']))}\t{title}\t{links}")
    return "\n".join(out)


def item_id(version, n, total):
    """項目の ID `<版>-<連番>`。連番は2桁ゼロ詰めで、100項目以上の版は3桁にする。"""
    return f"{version}-{n:0{3 if total >= 100 else 2}d}"


def render_text(d):
    out = [f"[{d['version']}] {d['date_iso']} | {d['title']}"]
    if d.get("warning"):
        out.append(f"!! WARNING: {d['warning']}")
    for p in d["intro"]:
        out.append(f"  {p}")

    def dump_sections(sections, indent):
        for s in sections:
            out.append(f"{indent}## {s['title'] or '(見出しなし)'}")
            for i in s["items"]:
                out.append(f"{indent}  - {i}")
            for g in s["groups"]:
                out.append(f"{indent}  * {g['label']}")
                for i in g["items"]:
                    out.append(f"{indent}    - {i}")

    dump_sections(d["sections"], "")
    for p in d["patches"]:
        out.append(f"\n--- {p['version']} ({p['date_iso']})")
        for l in p["lines"]:
            out.append(f"    {l}")
        dump_sections(p["sections"], "    ")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+", help="取得済みの changelog HTML")
    ap.add_argument("--text", action="store_true", help="JSON ではなく可読形式で出力")
    ap.add_argument("--items", action="store_true",
                    help="項目（ID・題・リンク）を版ごとに1行ずつ出力（渡したページだけで版の取り出し元を選ぶ）")
    args = ap.parse_args()

    failed = 0
    results = []
    ok_paths = []
    for path in args.files:
        d = extract(path)
        if not d["title"]:
            print(f"ERROR: {path}: 本文を抽出できませんでした"
                  "（ページ構造の変化を疑ってください）", file=sys.stderr)
            failed += 1
            continue
        if d.get("warning"):
            print(f"WARNING: {path}: {d['warning']}", file=sys.stderr)
        if args.items:
            ok_paths.append(path)
            results.append(d)
        elif args.text:
            print(render_text(d))
        else:
            results.append(d)
    if args.items:
        print(render_items(releases(ok_paths, results)))
        return 1 if failed else 0
    # JSON は配列で一括出力する。ページごとにオブジェクトを並べると
    # 複数ファイルを渡したときに JSON として読めなくなる（オブジェクトの連結になる）。
    if not args.text:
        print(json.dumps(results, ensure_ascii=False, indent=1))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
