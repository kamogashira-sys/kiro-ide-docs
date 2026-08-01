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

重要な前提（`05_meta/10_version-update-guide.md` §3・§5 と対応）:

- ページ左の「Latest Patches」ブロックにある `"patches":[{id,version,date}]` は
  **ナビゲーションの索引**であり、version と date しか持たない。
  **パッチの説明文は本文側の別ノード `<div id="patch-X-Y-Z">` に存在する。**
  索引に説明が無いことを「説明が存在しない」と読み替えてはならない。
- 網羅性（全パッチの列挙）は索引で担保し、記述内容は本文ノードで判断する。
"""
import argparse
import json
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

        if tag == "li":
            t = clean(text_of(props.get("children"), table))
            if t:
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
    acc = {"intro": [], "sections": [], "patches": [], "cur_patch": None}
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
    }
    # 索引と本文のパッチ数が食い違ったら構造変化の可能性がある
    if index is not None and len(index) != len(acc["patches"]):
        result["warning"] = (
            f"索引 {len(index)} 件に対し本文ノード {len(acc['patches'])} 件"
            "（ページ構造が変わった可能性あり）"
        )
    return result


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
    args = ap.parse_args()

    failed = 0
    results = []
    for path in args.files:
        d = extract(path)
        if not d["title"]:
            print(f"ERROR: {path}: 本文を抽出できませんでした"
                  "（ページ構造の変化を疑ってください）", file=sys.stderr)
            failed += 1
            continue
        if d.get("warning"):
            print(f"WARNING: {path}: {d['warning']}", file=sys.stderr)
        if args.text:
            print(render_text(d))
        else:
            results.append(d)
    # JSON は配列で一括出力する。ページごとにオブジェクトを並べると
    # 複数ファイルを渡したときに JSON として読めなくなる（オブジェクトの連結になる）。
    if not args.text:
        print(json.dumps(results, ensure_ascii=False, indent=1))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
