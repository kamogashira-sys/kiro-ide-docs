#!/usr/bin/env python3
"""check-impact.py - PR 本文の対応表を、版更新の影響範囲と突き合わせて検査する（T2）

使用方法:
    # PR を作る前（基本。クラウドとローカルの版更新）
    ./scripts/kiro-ide-docs/check-impact.py --html-dir /tmp/kiro-ide-primary \\
        --pr-body .kiro/cloud-runs/<run_id>/pr-body.md [--base origin/<base>] [--versions V,...]

    # PR を作った後（補助。PC での確認・人が本文を直した後の再確認）
    ./scripts/kiro-ide-docs/check-impact.py --html-dir /tmp/kiro-ide-primary --pr <番号>

    make check-kiro-ide-impact PR_BODY=<file> [BASE=origin/<base>]   # 末尾に impact-check-result: rc=N
    make check-kiro-ide-cloud PR_BODY=<file> BASE=origin/<base>       # 一括検証の中で実行する

何を検査するか:
    `impact-report.py` の analyze()（T1 と同じ関数）で版の項目を作り直し、PR 本文の表
    （見出し行に `ID`・`changelog 項目`・`対応` の列を持つ表）の行を ID で照合する。
    - 行が無い・同じ ID が2行・T1 に無い ID・`changelog 項目` の先頭20字が一次情報と違う
    - 「対応」の値と、その根拠（下記）
    - `削除・書き換えた既存の記述` 節に、T3 の「表ごと消えた」「列が消えた」「消えた行」の判断
      （`判断: 消す: https://kiro.dev/…` か `判断: 要判断: <理由>`）があること

「対応」に許す値（正はこのスクリプト。手順書 §6.6 の手順5a・5b・6 に写してある）:
    反映した   `反映した: <ファイル> §<節>[、<ファイル> §<節>…]`。ファイルが起点から変わり、§<節> の下に
               `#v<版>` を含む追加行がある。区分が「強」系なら、ファイルが公式ページを引用していて、
               節が引用のある最上位の節に入る。出典行だけで引用するファイルでは、§<節> の追加行の
               どれかが検索語か公式 URL を含む。公式の節にあって本サイトに無い語が0個
    変更不要   `変更不要: <ファイル>:<行> 「<本サイトの文>」＝公式「<公式の節の文>」`。公式の節を
               切り出せた行だけ。2つの文（10字以上）が実在し、行が引用のある節の中にあり、無い語が0個
    該当箇所なし 区分「なし」で本文の件数が0なら理由なしでよい。本文に当たる「なし」は理由に検索語を
               含む `ファイル:行`、「見出しのみ」「強」は理由に候補の `ファイル:行` が要る
    未確認     `未確認: <理由>`。区分「強・版以後」では不可。候補がある行は理由に候補の
               `ファイル:行`、PR 本文の「未確認・据え置き」節の箇条にその ID が要る
    区分「強・版以後」の行は「反映した」か「変更不要」だけ。「強（節なし）」は「反映した」か「未確認」。

出力:
    エラーは1件ずつ `❌ <ID>: <理由>`。次に合格した「変更不要」の一覧（`変更不要: …`）と、出典行だけの
    ファイルで合格した「反映した」の一覧（`反映した（出典行だけ）: …`）。最後の行は
    `対応表: 項目 N / 行 N / 反映した N / 変更不要 N / 該当箇所なし N / 未確認 N / 削除の判断 N（消す N / 要判断 N） / エラー N`。
    この3つを PR 本文の「検証結果」に入れる（手順書 §14.3 の手順 D が入れる）。

exit コード:
    0 … 合格。または版更新ではない
    1 … 対応表の不備（本文か文書を直せば通る）。版更新なのに本文が渡されていない
    2 … 使い方の誤り・前提の崩れ（引数・`--pr` と `--pr-body` の両方・`--pr` で作業ツリーが汚れている／
         HEAD が PR の head と違う／`--base` が PR の base と違う・changelog が変わっているのに版の差が無い）
    3 … 未検証（一次情報・公式機能ページ・gh の取得失敗、項目を取り出せない、BASE を解決できない、
         shallow clone、BASE と HEAD の共通の祖先が無い）
    make はレシピの非0を exit 2 にするので、`impact-check-result: rc=N` の行で判定する。

PR 本文は判定の対象のデータとしてだけ扱い、実行しない。外部の値（PR 番号・パス）はシェルを通さず
引数リストで渡す。gh は REST（`gh api repos/<GH_REPO_SLUG>/pulls/N`）だけを使う。
"""
import argparse
import collections
import importlib.util
import json
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GH_REPO_SLUG = "kamogashira-sys/kiro-ide-docs"


def load_impact_report():
    spec = importlib.util.spec_from_file_location("impact_report", os.path.join(SCRIPT_DIR, "impact-report.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ir = load_impact_report()
Fail = ir.Fail

ID_RE = re.compile(r'^\d+\.\d+(?:\.\d+)?-\d{2,3}$')
IDS = r'\d+\.\d+(?:\.\d+)?-\d{2,3}'
FILE = r'((?:kiro-ide-docs/)?0[0-4]_[a-z0-9_-]+/[A-Za-z0-9._-]+\.md)'
LOC_RE = re.compile(FILE + r':(\d+)')
VALUE_RE = re.compile(r'^(反映した|変更不要|該当箇所なし|未確認)(?:[:：]\s*(.*))?$')
UNCHANGED_RE = re.compile(FILE + r':(\d+)\s*「(.+?)」\s*[＝=]\s*公式「(.+?)」\s*$')
PIPE_RE = re.compile(r'(?<!\\)\|')
PR_RE = re.compile(r'^[1-9][0-9]{0,6}$')
PENDING_SECTION = "未確認・据え置き"
REMOVED_SECTION = "削除・書き換えた既存の記述"
JUDGE_RE = re.compile(r'判断:\s*(消す:\s*https://kiro\.dev/\S+|要判断:\s*\S+)')
MIN_QUOTE = 10
QUOTE_MAX = 100


def full(f):
    return f if f.startswith("kiro-ide-docs/") else "kiro-ide-docs/" + f


def norm_ws(s):
    return re.sub(r'\s+', ' ', s).strip()


def plain(s):
    return norm_ws(re.sub(r'(\*\*|`|\[|\]\([^)]*\))', '', s))


# ------------------------------------------------------------
# PR 本文の解析
# ------------------------------------------------------------
def parse_table(body):
    """見出し行に ID と 対応 を持つ表の行。({ID: {列: 値}}, 重複した ID, 表があったか)"""
    rows, dup, found, hdr = {}, [], False, None
    for l in body.split("\n"):
        if not l.lstrip().startswith("|"):
            if not l.strip():
                hdr = None
            continue
        c = [x.strip().replace("\\|", "|") for x in PIPE_RE.split(l.strip().strip("|"))]
        if "ID" in c and "対応" in c:
            hdr, found = c, True
            continue
        if hdr and c and ID_RE.match(c[0]):
            if c[0] in rows:
                dup.append(c[0])
            rows[c[0]] = dict(zip(hdr, c))
    return rows, dup, found


def md_section(body, name):
    """見出しの文字列が name の行から、同じ階層かそれより上の次の見出しまでの行（下位の見出しの中も含む）。"""
    out, lvl = None, None
    for l in body.split("\n"):
        m = re.match(r'^(#{1,6})\s+(.*?)\s*$', l)
        if out is None:
            if m and m.group(2) == name:
                out, lvl = [], len(m.group(1))
            continue
        if m and len(m.group(1)) <= lvl:
            break
        out.append(l)
    return out or []


def pending_ids(body):
    """「未確認・据え置き」節の、`- <ID>[・<ID>…]` で始まる箇条の先頭の ID（文中・表の中は数えない）。"""
    ids = set()
    for l in md_section(body, PENDING_SECTION):
        m = re.match(r'^\s*[-*]\s*(' + IDS + r'(?:\s*[・、,]\s*' + IDS + r')*)', l)
        if m:
            ids |= set(re.findall(IDS, m.group(1)))
    return ids


# ------------------------------------------------------------
# 規則
# ------------------------------------------------------------
def sec_of(lines, n):
    """n 行目（1始まり）が属する節の番号（その行か上にある最も近い `#… <番号>` の見出し）。"""
    for i in range(n - 1, -1, -1):
        m = re.match(r'^#+\s+([\d.]+)', lines[i])
        if m:
            return m.group(1).rstrip(".")
    return ""


def in_section(lines, n, s):
    sec = sec_of(lines, n)
    return sec == s or sec.startswith(s + ".")


def cite_tops(x, lines):
    """そのファイルで公式ページを引用している行の、最上位の節番号の集合（出典行だけなら空）。"""
    paths = {o["path"] for o in x["official"] if o["cited_by"]}
    return {sec_of(lines, n).split(".")[0] for n, l in enumerate(lines, 1)
            if any(ir.norm_path(m.group(1)) in paths for m in ir.SITE_URL_RE.finditer(l))} - {""}


def item_line(x, line):
    """行がその項目の検索語か公式ページの URL を含む（大文字小文字を区別しない部分一致）。"""
    low = line.lower()
    urls = ["kiro.dev" + o["path"].rstrip("/") for o in x["official"] if o["cited_by"]]
    if any(u.lower() in low for u in urls):
        return True
    return any(t.lower() in low for t in x["terms"])


class Checker:
    def __init__(self, B, changed, pending):
        self.B, self.changed, self.pending = B, changed, pending
        self.texts = {}
        self.unchanged, self.sourceonly = [], []

    def lines(self, f):
        if f not in self.texts:
            self.texts[f] = ir.lines_of(None, f)
        return self.texts[f]

    def locs_ok(self, i, locs, allowed, E):
        ok = []
        for f, n in locs:
            ff = full(f)
            txt = self.lines(ff)
            if not (txt != [""] and 1 <= int(n) <= len(txt)):
                E.append(f"{i}: {f}:{n} は行の範囲外")
                continue
            if allowed(ff, txt[int(n) - 1]):
                ok.append((ff, int(n)))
        return ok

    def row(self, x, v):
        i, k, E = x["id"], x["class"], []
        m = VALUE_RE.match(v)
        if not m:
            return [f"{i}: 対応の値が規定外: 「{v}」"]
        kind, reason = m.group(1), (m.group(2) or "").strip()
        if kind == "反映した":
            return self.reflected(x, reason)
        if kind == "変更不要":
            return self.unchanged_row(x, reason)
        if k == "strong_after_release":
            return [f"{i}: 公式の節（版以後に更新）を本サイトが引用しているので {kind} は不可（反映した か 変更不要）"]
        miss = [w for w in x["missing"] if w.lower() not in v.lower()]
        if miss:
            E.append(f"{i}: {kind} の欄に、公式の節にあって本サイトに無い語が挙がっていない: {miss}")
        locs = LOC_RE.findall(reason)
        if kind == "該当箇所なし":
            if k == "strong_nosection":
                return E + [f"{i}: 区分「強（節なし）」では 該当箇所なし は不可（反映した か 未確認）"]
            if k == "none" and x["body_count"] == 0:
                return E
            if k == "none":
                rx = [ir.term_regex(t) for t in x["terms"]]
                if not self.locs_ok(i, locs, lambda ff, line: any(r.search(line) for r in rx), E):
                    E.append(f"{i}: 該当箇所なし の理由に、検索語が当たった本文の「ファイル:行」が無い"
                             f"（本文 {x['body_count']} 件）")
            elif not self.locs_ok(i, locs, lambda ff, line: ff in x["candidates"], E):
                E.append(f"{i}: 該当箇所なし の理由に候補の「ファイル:行」が無い")
            return E
        # 未確認
        if x["candidates"] and not self.locs_ok(i, locs, lambda ff, line: ff in x["candidates"], E):
            E.append(f"{i}: 未確認 の理由に候補の「ファイル:行」が無い")
        if i not in self.pending:
            E.append(f"{i}: 未確認 だが「{PENDING_SECTION}」の箇条に ID が無い")
        return E

    def reflected(self, x, reason):
        i, E, found = x["id"], [], []
        secs = re.findall(FILE + r'\s*§\s*([\d.]+)', reason)
        if not secs:
            return [f"{i}: 反映した は「<ファイル> §<節>」が要る"]
        tag = "#v" + x["version"].replace(".", "-")
        strong = x["class"].startswith("strong")
        for f, s in secs:
            ff, s = full(f), s.rstrip(".")
            if ff not in self.changed:
                E.append(f"{i}: 反映した {f} は起点（merge-base）から変更されていない")
                continue
            txt = self.lines(ff)
            tops = cite_tops(x, txt) if strong else set()
            if strong:
                if ff not in x["cited_files"]:
                    E.append(f"{i}: 反映した {f} は、この項目の公式ページを引用するファイルではない")
                    continue
                if tops and s.split(".")[0] not in tops:
                    E.append(f"{i}: 反映した {f} §{s} は、公式ページを引用している節（§{'・§'.join(sorted(tops))}）の外")
                    continue
            tagged = ir.added_lines(self.B, ff, tag)
            ins = [n for n in tagged if in_section(txt, n, s)]
            if not ins:
                E.append(f"{i}: 反映した {f} §{s} に {tag} を含む追加行が無い（追加行 {tagged}）")
                continue
            if strong and not tops:
                # 出典行だけで引用するファイル: §<節> の追加行（追加・変更した見出しを含む）に検索語か URL
                hit = [n for n in ir.added_lines(self.B, ff) if in_section(txt, n, s) and item_line(x, txt[n - 1])]
                if hit:
                    found.append((f, s, hit[0], txt[hit[0] - 1]))
                else:
                    E.append(f"{i}: 反映した {f} §{s}: 出典行だけで引用するファイルなので、§{s} の追加行に"
                             f"この項目の検索語か公式 URL が要る（{tag} の追加行 {ins}）")
        if x["missing"]:
            E.append(f"{i}: 反映した だが、公式の節にあって本サイトに無い語が残る: {x['missing']}")
        if not E:
            for f, s, n, line in found:
                q = norm_ws(line)
                q = q if len(q) <= QUOTE_MAX else q[:QUOTE_MAX - 1] + "…"
                self.sourceonly.append(f"反映した（出典行だけ）: {i} {f} §{s} L{n} 「{q}」")
        return E

    def unchanged_row(self, x, reason):
        i, E = x["id"], []
        if not x["sections"]:
            return [f"{i}: 変更不要 は公式の節の抜粋がある行だけに使える"]
        mm = UNCHANGED_RE.match(reason)
        if not mm:
            return [f"{i}: 変更不要 の書式は「<ファイル>:<行> 「<本サイトの文>」＝公式「<公式の文>」」"]
        f, n, a, b = mm.groups()
        if len(a) < MIN_QUOTE or len(b) < MIN_QUOTE:
            E.append(f"{i}: 変更不要 の引用は{MIN_QUOTE}字以上")
        ok = self.locs_ok(i, [(f, n)], lambda ff, line: ff in x["cited_files"], E)
        if not ok:
            E.append(f"{i}: 変更不要 の {f}:{n} は公式の節を引用するファイルの行ではない")
        else:
            txt = self.lines(ok[0][0])
            line = txt[ok[0][1] - 1]
            tops = cite_tops(x, txt)
            if tops and sec_of(txt, ok[0][1]).split(".")[0] not in tops:
                E.append(f"{i}: 変更不要 の {f}:{n} は、公式ページを引用している節（§{'・§'.join(sorted(tops))}）"
                         f"の外（§{sec_of(txt, ok[0][1]) or 'なし'}）")
            elif not tops and not item_line(x, line):
                E.append(f"{i}: 変更不要 の {f}:{n}: 出典行だけで引用するファイルなので、行にこの項目の検索語か公式 URL が要る")
            if norm_ws(a) not in norm_ws(line) and plain(a) not in plain(line):
                E.append(f"{i}: 変更不要 の本サイトの文が {f}:{n} に無い")
        if not any(norm_ws(b) in s for s in x["sections"]):
            E.append(f"{i}: 変更不要 の公式の文が公式の節に無い")
        if x["missing"]:
            E.append(f"{i}: 変更不要 だが、公式の節にあって本サイトに無い語が残る: {x['missing']}")
        if not E:
            self.unchanged.append(f"変更不要: {i} {f}:{n} 「{a}」＝公式「{b}」")
        return E


def check_removed(body, B):
    need, _, _ = ir.removed(B)
    sec = md_section(body, REMOVED_SECTION)
    E, kinds = [], collections.Counter()
    for f, n, k, _ in need:
        pre = re.compile(r'^\s*[-*]\s*(?:kiro-ide-docs/)?' + re.escape(ir.short(f)) + rf'\s+L{n}\s+{k}\b')
        hit = [l for l in sec if pre.match(l)]
        if not hit:
            E.append(f"{ir.short(f)} L{n} {k}: 「{REMOVED_SECTION}」に行が無い")
            continue
        ms = [m for m in (JUDGE_RE.search(l) for l in hit) if m]
        if not ms:
            E.append(f"{ir.short(f)} L{n} {k}: 判断（消す: <公式 URL> か 要判断: <理由>）が無い")
        else:
            kinds["消す" if ms[0].group(1).startswith("消す") else "要判断"] += 1
    return E, len(need), kinds


# ------------------------------------------------------------
# PR の取得（--pr）
# ------------------------------------------------------------
def fetch_pr(n):
    r = subprocess.run(["gh", "api", f"repos/{GH_REPO_SLUG}/pulls/{n}"], capture_output=True, text=True)
    if r.returncode:
        lines = [l for l in r.stderr.strip().split("\n") if l.strip()]
        raise Fail(3, lines[-1] if lines else f"gh api が失敗しました（rc={r.returncode}）")
    try:
        pr = json.loads(r.stdout)
        return pr.get("body") or "", pr["base"]["ref"], pr["head"]["sha"]
    except (ValueError, KeyError, TypeError):
        raise Fail(3, "gh api の応答から PR の本文・base・head を読めません")


def pr_context(a):
    """--pr の前提の検査。返り値は (本文, BASE)。"""
    body, base_ref, head_sha = fetch_pr(a.pr)
    if ir.git("status", "--porcelain", "--", "kiro-ide-docs", ".github/release-notes").strip():
        raise Fail(2, "作業ツリーに PR に無い変更があります（git status を確認）")
    if ir.git("rev-parse", "HEAD").strip() != head_sha:
        raise Fail(2, f"検査する木（HEAD）が PR の head（{head_sha[:7]}）と違います")
    base = "origin/" + base_ref
    pr_base = ir.resolve_commit(base)
    if pr_base is None:
        raise Fail(3, f"BASE を解決できません: {base}（clone に参照が無い。git fetch を確認）")
    if a.base:
        given = ir.resolve_commit(a.base)
        if given is None:
            raise Fail(3, f"BASE を解決できません: {a.base}（clone に参照が無い。git fetch を確認）")
        if given != pr_base:
            raise Fail(2, f"--base {a.base} が PR の base（{base}）と違います")
    return body, base


def read_body(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        raise Fail(2, f"--pr-body を読めません: {path}（{e.strerror}）")
    except UnicodeDecodeError:
        raise Fail(2, f"--pr-body が UTF-8 ではありません: {path}")


def run(a):
    ir.check_html_dir(a.html_dir)
    if a.versions:
        ir.check_versions_arg(a.versions)
    if a.pr and a.pr_body:
        raise Fail(2, "--pr と --pr-body はどちらか1つにしてください")
    if a.pr and not PR_RE.match(a.pr):
        raise Fail(2, f"PR 番号の形式が違います: {a.pr}")
    body = read_body(a.pr_body) if a.pr_body else None
    base = a.base or ir.DEFAULT_BASE
    if a.pr:
        body, base = pr_context(a)
    B = ir.merge_base(base)
    print(f"起点（merge-base）: {B[:7]}（BASE {base}）")
    wanted = ir.target_versions(B, a.versions)
    if wanted is None:
        print(ir.NOT_UPDATE_MSG)
        return 0
    if body is None:
        raise Fail(1, "版更新なので PR 本文（--pr-body）が要ります")
    rel = ir.load_releases(a.html_dir)
    versions = ir.resolve_versions(wanted, rel)
    print(f"版: {', '.join(versions)}")
    pages = ir.OfficialPages()
    try:
        items, failures = ir.analyze(B, versions, rel, pages)
    finally:
        pages.close()
    if failures:
        for url in dict.fromkeys(f"{p['url']} HTTP {p['http']}" for p in failures):
            print(f"⚠ 取得失敗: {url}")
        raise Fail(3, "公式機能ページを取得できないので検査できません（未検証）")
    rows, dup, found = parse_table(body)
    if not found:
        raise Fail(1, "ID と 対応 の列を持つ表がありません")
    chk = Checker(B, ir.changed_files(B), pending_ids(body))
    E = [f"{d}: 同じ ID の行が複数" for d in dup]
    ids = {x["id"] for x in items}
    E += [f"{i}: T1 に無い ID" for i in rows if i not in ids]
    stat, mism = collections.Counter(), 0
    for x in items:
        i = x["id"]
        if i not in rows:
            E.append(f"{i}: 行が無い（{(x['title'] or x['body'])[:40]}）")
            continue
        t = (x["title"] or x["body"])[:20]
        c = rows[i].get("changelog 項目")
        if c is None:
            E.append(f"{i}: changelog 項目 列が要る（先頭20字でよい）")
            continue
        if c[:20] != t:
            E.append(f"{i}: changelog 項目の題が一次情報と違う（{c[:20]} ≠ {t}）")
            mism += 1
            continue
        v = rows[i].get("対応", "").strip()
        stat[re.split(r'[:：]', v, maxsplit=1)[0]] += 1
        E += chk.row(x, v)
    if mism >= 2:
        E.append("ID がずれています（一次情報が T1 の後に変わった疑い）。T1 をやり直してください")
    RE, nneed, kinds = check_removed(body, B)
    E += RE
    for e in E:
        print("❌", e)
    for u in chk.unchanged:
        print(u)
    for u in chk.sourceonly:
        print(u)
    print(f"対応表: 項目 {len(items)} / 行 {len(rows)} / 反映した {stat['反映した']} / 変更不要 {stat['変更不要']} / "
          f"該当箇所なし {stat['該当箇所なし']} / 未確認 {stat['未確認']} / "
          f"削除の判断 {nneed}（消す {kinds['消す']} / 要判断 {kinds['要判断']}） / エラー {len(E)}")
    return 1 if E else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--html-dir", required=True, help="取得済み changelog HTML のディレクトリ")
    ap.add_argument("--versions", help="版（カンマ区切り）。無ければ changelog の目次の差")
    ap.add_argument("--base", help=f"起点を決める BASE（既定 {ir.DEFAULT_BASE}。--pr では PR の base）")
    ap.add_argument("--pr-body", help="PR 本文のファイル（UTF-8）")
    ap.add_argument("--pr", help="PR 番号（gh api で本文を取る）")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    os.chdir(ir.repo_root())
    try:
        return run(a)
    except Fail as e:
        return ir.report(e)


if __name__ == "__main__":
    sys.exit(main())
