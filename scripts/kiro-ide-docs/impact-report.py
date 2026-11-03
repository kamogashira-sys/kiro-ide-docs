#!/usr/bin/env python3
"""impact-report.py - 版更新の影響範囲を出す（対応表の雛形・削除された記述・公式の節の切り出し）

使用方法:
    # T1: 加わった版の changelog の項目ごとに、本サイトの候補を並べた対応表の雛形を出す
    ./scripts/kiro-ide-docs/impact-report.py table --html-dir /tmp/kiro-ide-primary \\
        [--versions 1.4.51,1.4.62] [--base origin/main] [--json OUT] [--no-excerpts]

    # T3: 起点（merge-base）から消えた表の列・表の行・文を、PR 本文に貼れる形で出す
    ./scripts/kiro-ide-docs/impact-report.py removed [--base origin/main] [--head REV]

    # 公式機能ページの1つの節を切り出す（手順書 §6.6.3）。--id '' で h2〜h4 の id の一覧
    ./scripts/kiro-ide-docs/impact-report.py section --url https://kiro.dev/docs/memory/ \\
        --id review-what-kiro-remembers

    make kiro-ide-impact VERSIONS=<版>      # T1（一次情報の取得から1回の make で行う）
    make kiro-ide-removed [BASE=<REV>]      # T3

起点:
    どのコマンドも、差分は B = `git merge-base <BASE> HEAD` から取る（BASE の先端と比べる
    2点の比較は使わない。base が先に進んでも、ブランチが変えていない行を拾わないため）。
    HEAD は作業ツリー（`removed --head` を渡したときはその木）。BASE の既定は `origin/main`。

版:
    `--versions` が無ければ、起点と作業ツリーの changelog の目次（`check-coverage.py` の
    `TOC_RE`）の差を加わった版とする。差が空で changelog も変わっていなければ「版更新では
    ありません」で exit 0。差が空なのに changelog が変わっていれば exit 2（BASE の取り違え）。
    `--versions` の各版と一次情報の版は、両側を `check-freshness.py` の `canon()` で正規化して
    比べる（`1.0` → `1.0.0`、`1.2` → `1.2.4`）。ID と表には一次情報の版を使う。

対応表の区分（T1 と `check-impact.py` が同じ関数 `analyze()` で決める）:
    強・版以後   … 項目のリンク先の公式ページを本サイトが引用していて、`Page updated` が版の
                   リリース日以後で、アンカーの節を切り出せた
    強（節なし） … 引用があり、リンクにアンカーがあるが、公式ページにその id の見出しが無い
    強           … 引用はあるが、更新日が取れないか版より前
    見出しのみ   … 引用は無く、検索語が本サイトの見出しに当たった
    なし         … どちらも無い
    引用は、起点の木と作業ツリーの両方の和で数える（執筆で引用行が増減しても区分が変わらない）。

環境変数:
    KIDE_DOCS_ORIGIN … 公式機能ページの取得元（既定 https://kiro.dev）。試験で取得先を
                       差し替えるときに使う（`check-freshness.py` の KIDE_*_URL と同じ形）

exit コード:
    0 … 出力した（T3 は常に 0）。版更新ではない
    1 … section: id が無い
    2 … 引数の誤り（版の形式・一次情報に無い版・HTML が無い・`--head` を解決できない）、
         changelog が変わっているのに版の差が取れない
    3 … 未検証。公式ページの取得失敗、changelog ページから項目を取り出せない、
         BASE を解決できない、shallow clone、BASE と HEAD の共通の祖先が無い

ネットワーク: table（版更新のときだけ）と section は公式機能ページを curl で取得し、
一時ディレクトリに置く。リポジトリには書かない。
"""
import argparse
import collections
import glob
import html as htmllib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_ORIGIN_DEFAULT = "https://kiro.dev"
UA = "Mozilla/5.0"
DEFAULT_BASE = "origin/main"

CHANGELOGS = [
    "kiro-ide-docs/02_update/01_changelog.md",
    "kiro-ide-docs/02_update/02_changelog-0x.md",
]
# 候補を探す範囲（手順書 §6.6 手順2 と同じ）。changelog・README・リリースノートは
# 版ごとに必ず更新するので候補に入れず、SYNC_TARGETS として別に出す
SCOPE = (
    "kiro-ide-docs/00_information/",
    "kiro-ide-docs/01_features/",
    "kiro-ide-docs/02_update/03_migration-to-1.0.md",
    "kiro-ide-docs/03_deployment/",
    "kiro-ide-docs/04_reference/",
)
SYNC_TARGETS = [
    "`README.md`",
    "`kiro-ide-docs/00_information/README.md`",
    "`kiro-ide-docs/02_update/README.md`",
    "`kiro-ide-docs/02_update/01_changelog.md`",
    "`kiro-ide-docs/03_deployment/01_installation.md`（旧版段落と基準バージョン行）",
]

# 本サイト側の kiro.dev の URL（http://・www. は本サイトに0行なので扱わない）
SITE_URL_RE = re.compile(r'https://kiro\.dev(/[^\s)\]>"\'`|<]*)')
PAGE_UPDATED_RE = re.compile(r'Page updated:<!-- --> <!-- -->([A-Za-z]+) (\d+), (\d{4})')
HEADING_RE = re.compile(r'#+ ')
VERSIONS_RE = re.compile(r'^\d+\.\d+(\.\d+)?(,\d+\.\d+(\.\d+)?)*$')
SLUG_RE = re.compile(r'(^|,)\d+-\d+(-\d+)?(,|$)')
SECTION_ID_RE = re.compile(r'^[a-z0-9-]*$')

# 検索語の止め語。題・本文の大文字で始まる語の連なりから除く
STOP = {"Kiro", "Fixed", "I", "A", "An", "The", "When", "If", "In", "On", "Now",
        "It", "This", "You", "Your", "To", "With"}
CAP_RUN_RE = re.compile(r"[A-Z][\w'+./-]*(?:\s+[A-Z][\w'+./-]*)*")
MIN_TERM = 3
BODY_HITS_PER_TERM = 5
HEADING_FILES_MAX = 6

CLASS_LABEL = {
    "strong_after_release": "強（URL 引用・公式更新が版以後）",
    "strong_nosection": "強（節なし）",
    "strong": "強（URL 引用）",
    "heading_only": "見出しのみ",
    "none": "なし",
}


class Fail(Exception):
    """exit code と1行の理由。code 3 は `⚠ `、それ以外は `❌ ` で出す。"""

    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code
        self.msg = msg


def report(e):
    print(("⚠ " if e.code == 3 else "❌ ") + e.msg)
    return e.code


def repo_root():
    return os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))


def load_script(name, modname):
    """ハイフン入りのスクリプトをモジュールとして読み込む（`check-coverage.py` の load_extractor と同じ方法）。"""
    spec = importlib.util.spec_from_file_location(modname, os.path.join(SCRIPT_DIR, name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ex = load_script("extract-changelog.py", "extract_changelog")
cov = load_script("check-coverage.py", "check_coverage")     # TOC_RE
fresh = load_script("check-freshness.py", "check_freshness")  # canon()


# ------------------------------------------------------------
# git と木の読み取り（rev が None なら作業ツリー）
# ------------------------------------------------------------
def git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and r.returncode:
        raise Fail(3, f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def read(rev, path):
    """ファイルの中身。無ければ None。"""
    if rev is None:
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except (OSError, UnicodeDecodeError):
            return None
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def lines_of(rev, path):
    return (read(rev, path) or "").split("\n")


def scope_files(rev):
    """候補を探す範囲の .md。作業ツリーは追跡中か ignore されていないファイルで、実在するもの。"""
    if rev is None:
        out = git("ls-files", "--cached", "--others", "--exclude-standard", "--", *SCOPE).split("\n")
        out = [f for f in dict.fromkeys(out) if f and os.path.isfile(f)]
    else:
        out = git("ls-tree", "-r", "--name-only", rev).split("\n")
    return sorted(f for f in out if f.endswith(".md") and f.startswith(SCOPE))


def short(path):
    return path[len("kiro-ide-docs/"):] if path.startswith("kiro-ide-docs/") else path


def resolve_commit(rev):
    r = subprocess.run(["git", "rev-parse", "--verify", "-q", f"{rev}^{{commit}}"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def merge_base(base):
    """起点 B = merge-base(BASE, HEAD)。clone の状態が原因の失敗は exit 3（未検証）。"""
    if resolve_commit(base) is None:
        raise Fail(3, f"BASE を解決できません: {base}（clone に参照が無い。git fetch を確認）")
    if git("rev-parse", "--is-shallow-repository").strip() == "true":
        raise Fail(3, "shallow clone なので起点（merge-base）を正しく計算できません")
    r = subprocess.run(["git", "merge-base", base, "HEAD"], capture_output=True, text=True)
    if r.returncode:
        raise Fail(3, "BASE と HEAD の共通の祖先がありません")
    return r.stdout.strip()


def changed_files(B, head=None):
    args = ["diff", "--name-only", B] + ([head] if head else [])
    return set(f for f in git(*args).split("\n") if f)


def added_lines(B, path, tag=None):
    """`git diff -U0 B -- path`（作業ツリーと比べる）の追加行の行番号。tag があればそれを含む行だけ。"""
    out, cur = [], None
    for x in git("diff", "-U0", B, "--", path).split("\n"):
        h = re.match(r'^@@ -\S+ \+(\d+)', x)
        if h:
            cur = int(h.group(1))
            continue
        if cur is None:
            continue
        if x.startswith("+") and not x.startswith("+++"):
            if tag is None or tag in x:
                out.append(cur)
            cur += 1
    return out


# ------------------------------------------------------------
# 版
# ------------------------------------------------------------
def toc_versions(rev):
    vs = set()
    for f in CHANGELOGS:
        for ln in lines_of(rev, f):
            m = cov.TOC_RE.match(ln)
            if m:
                vs.add(m.group(1))
    return vs


def load_releases(html_dir):
    """一次情報の HTML から {版: [候補コンテナ]}。抽出できないページがあれば exit 3。"""
    files = sorted(glob.glob(os.path.join(html_dir, "*.html")))
    pages = []
    for path in files:
        d = ex.extract(path)
        if not d["title"]:
            raise Fail(3, f"{path}: 本文を抽出できませんでした（ページ構造の変化を疑ってください）")
        pages.append(d)
    return ex.releases(files, pages)


def check_html_dir(html_dir):
    if not html_dir or not os.path.isdir(html_dir) or not glob.glob(os.path.join(html_dir, "*.html")):
        raise Fail(2, f"{html_dir} に HTML がありません")


def check_versions_arg(arg):
    if SLUG_RE.search(arg):
        raise Fail(2, f"版番号で指定してください（スラッグ: {arg}）")
    if not VERSIONS_RE.match(arg):
        raise Fail(2, f"--versions の形式が違います: {arg}（例 1.4.51,1.4.62）")


def resolve_versions(wanted, rel):
    """両側を canon() で正規化して比べ、一次情報の版（extract() の version）を返す。"""
    by = {}
    for v in rel:
        by.setdefault(fresh.canon(v), v)
    out = []
    for v in wanted:
        hit = by.get(fresh.canon(v))
        if not hit:
            raise Fail(2, f"一次情報に無い版: {v}")
        if hit in out:
            print(f"⚠ 重複した版をまとめました: {v}", file=sys.stderr)
            continue
        out.append(hit)
    return out


def target_versions(B, versions_arg):
    """調べる版の一覧（一次情報に当てる前）。版更新でなければ None。"""
    if versions_arg:
        return versions_arg.split(",")
    vs = sorted(toc_versions(None) - toc_versions(B), key=ex.version_key)
    if vs:
        return vs
    if git("diff", "--name-only", B, "--", *CHANGELOGS).strip():
        raise Fail(2, "changelog が変わっているのに版の差が取れません（BASE を確認）")
    return None


NOT_UPDATE_MSG = "起点..作業ツリーで changelog に加わった版がありません（版更新ではありません）"


# ------------------------------------------------------------
# 公式機能ページ
# ------------------------------------------------------------
def norm_path(path):
    """kiro.dev のパスの正規化: クエリとアンカーを外す → .md を外す → /index を外す → 末尾に /。"""
    p = path.split("#", 1)[0].split("?", 1)[0]
    if p.endswith(".md"):
        p = p[:-3]
    if p.endswith("/index"):
        p = p[:-len("/index")]
    if not p.endswith("/"):
        p += "/"
    return p


def anchor_of(path):
    return path.split("#", 1)[1] if "#" in path else None


def docs_origin():
    o = os.environ.get("KIDE_DOCS_ORIGIN") or DOCS_ORIGIN_DEFAULT
    if not re.match(r'^https?://[^/\s]+$', o.rstrip("/")):
        raise Fail(2, f"KIDE_DOCS_ORIGIN の形式が違います: {o}")
    return o.rstrip("/")


class OfficialPages:
    """公式機能ページを curl で1回ずつ取得し、一時ディレクトリに置く。"""

    def __init__(self):
        self.origin = docs_origin()
        self.tmp = tempfile.TemporaryDirectory(prefix="kiro-ide-impact-")
        self.cache = {}

    def get(self, path):
        """{"url", "http", "html"}。200 以外は html が None。"""
        if path in self.cache:
            return self.cache[path]
        url = self.origin + path
        fn = os.path.join(self.tmp.name, f"{len(self.cache)}.html")
        try:
            r = subprocess.run(["curl", "-sSL", "-A", UA, "--max-time", "30", "-o", fn,
                                "-w", "%{http_code}", url], capture_output=True, text=True)
        except FileNotFoundError:
            raise Fail(3, "curl が見つかりません（PATH を確認）")
        code = r.stdout.strip() or "000"   # curl は接続できないと 000 を出す
        page = {"url": url, "http": code, "html": None}
        if r.returncode == 0 and code == "200":
            with open(fn, encoding="utf-8", errors="replace") as f:
                page["html"] = f.read()
        self.cache[path] = page
        return page

    def close(self):
        self.tmp.cleanup()


def page_updated(html):
    """`Page updated: Oct 29, 2026` を ISO に。無ければ None（`/downloads/` は0件）。"""
    m = PAGE_UPDATED_RE.search(html or "")
    return ex.to_iso(f"{m.group(1)} {m.group(2)}, {m.group(3)}") if m else None


def visible_html(html):
    v = html[:html.find("self.__next_f")] if "self.__next_f" in html else html
    return re.sub(r'<(script|style)[^>]*>.*?</\1>', '', v, flags=re.S)


def heading_ids(html):
    v = visible_html(html)
    return v, [(m.start(), int(m.group(1)), m.group(2))
               for m in re.finditer(r'<h([2-4]) id="([^"]+)"', v)]


def section_html(html, sec_id):
    """アンカーの h2〜h4 から、同じか上の階層の次の見出しまでの HTML。(level, fragment) か (None, None)。"""
    v, hs = heading_ids(html)
    for k, (pos, lvl, i) in enumerate(hs):
        if i == sec_id:
            end = next((q for q, l2, _ in hs[k + 1:] if l2 <= lvl), len(v))
            return lvl, v[pos:end]
    return None, None


def fragment_text(fragment):
    s = re.sub(r'<(br|/p|/li|/h\d|/tr|/td|/th)[^>]*>', '\n', fragment)
    return re.sub(r'\n\s*\n+', '\n', htmllib.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def fragment_terms(fragment):
    """節の `<strong>`・`<code>`・`<kbd>` の文字列（3字以上）。`<pre>` の中（複数行のコード例）は除く。"""
    out = []
    s = re.sub(r'<pre[^>]*>.*?</pre>', '', fragment, flags=re.S)
    for m in re.finditer(r'<(strong|code|kbd)[^>]*>(.*?)</\1>', s, flags=re.S):
        t = re.sub(r'\s+', ' ', htmllib.unescape(re.sub(r'<[^>]+>', '', m.group(2)))).strip()
        if len(t) >= MIN_TERM and t not in out:
            out.append(t)
    return out


# ------------------------------------------------------------
# 本サイト側の索引（1つの木）
# ------------------------------------------------------------
class Tree:
    def __init__(self, rev):
        self.rev = rev
        self.files = scope_files(rev)
        self.lines = {f: lines_of(rev, f) for f in self.files}
        self.cites = collections.defaultdict(list)   # 正規化したパス -> [(file, line)]
        self.headings = []                            # [(file, line, text)]
        for f in self.files:
            for n, l in enumerate(self.lines[f], 1):
                if HEADING_RE.match(l):
                    self.headings.append((f, n, l))
                for m in SITE_URL_RE.finditer(l):
                    if not m.group(1).startswith("/changelog/"):
                        self.cites[norm_path(m.group(1))].append((f, n))


def term_regex(term):
    return re.compile(r'(?<![A-Za-z0-9])' + re.escape(term) + r'(?![A-Za-z0-9])', re.I)


def item_terms(it):
    """検索語: 題の大文字で始まる語の連なり（先頭の語を除く）か、題が無ければ本文の連なり（文頭の語を
    除く）と、項目の `<strong>`・`<code>`。止め語と3字未満を除く。"""
    out = []
    if it["title"]:
        for m in CAP_RUN_RE.finditer(it["title"]):
            if m.start() == 0:
                rest = m.group(0).split()[1:]
                if not rest:
                    continue
                cand = " ".join(rest)
            else:
                cand = m.group(0)
            if cand not in STOP:
                out.append(cand)
    else:
        body = it["body"]
        for m in CAP_RUN_RE.finditer(body):
            pre = body[:m.start()].rstrip()
            if not pre or pre.endswith((".", "!", "?", ":")):
                cand = " ".join(m.group(0).split()[1:])
                if not cand:
                    continue
            else:
                cand = m.group(0)
            if cand and cand not in STOP and cand not in out:
                out.append(cand)
    return [t for t in dict.fromkeys(out + it["terms"]) if len(t) >= MIN_TERM]


def official_links(it):
    """項目のリンクのうち kiro.dev の changelog 以外を、`/` で始まるパスにしたもの（出現順・重複なし）。"""
    out = []
    for l in it["links"]:
        h = l["href"]
        if h.startswith("https://kiro.dev"):
            h = h[len("https://kiro.dev"):]
        if h.startswith("/") and not h.startswith("/changelog/") and h not in out:
            out.append(h)
    return out


def analyze(B, versions, rel, pages):
    """T1・T2 共通: 版の項目ごとに、公式の節・本サイトの候補・区分・無い語を計算する。

    引用と見出しの候補は、起点 B と作業ツリーの和で数える。件数・本文の当たり・無い語は作業ツリー。
    """
    base, work = Tree(B), Tree(None)
    out, failures = [], []
    for v in versions:
        c = ex.pick_release(rel[v])
        if not c["items"]:
            raise Fail(3, f"{c['slug']}.html: 本文を抽出できませんでした（ページ構造の変化を疑ってください）")
        reldate = c["date_iso"]
        for n, it in enumerate(c["items"], 1):
            x = {"id": ex.item_id(v, n, len(c["items"])), "version": v, "release_date": reldate,
                 "source": f"{c['kind']}:{c['slug']}", "title": it["title"], "body": it["body"],
                 "official": [], "terms": item_terms(it)}
            for h in official_links(it):
                p = norm_path(h)
                page = pages.get(p)
                anc = anchor_of(h)
                o = {"href": h, "path": p, "anchor": anc, "http": page["http"], "updated": None,
                     "section_level": None, "section_text": None, "section_terms": [],
                     "cited_by": sorted(set(base.cites.get(p, [])) | set(work.cites.get(p, [])),
                                        key=lambda t: (t[0], t[1]))}
                if page["html"] is None:
                    failures.append(page)
                else:
                    o["updated"] = page_updated(page["html"])
                    if anc:
                        lvl, frag = section_html(page["html"], anc)
                        if lvl:
                            o["section_level"] = lvl
                            o["section_text"] = fragment_text(frag)
                            o["section_terms"] = fragment_terms(frag)
                o["after"] = bool(o["updated"] and reldate and o["updated"] >= reldate)
                x["official"].append(o)
            hits = []
            for tr in (work, base):
                for t in x["terms"]:
                    rx = term_regex(t)
                    for f, ln, l in tr.headings:
                        if rx.search(l):
                            h = {"term": t, "file": f, "line": ln, "heading": l.strip()}
                            if h not in hits:
                                hits.append(h)
            x["heading_hits"] = hits
            x["term_counts"], x["body_hits"] = {}, []
            for t in x["terms"]:
                rx = term_regex(t)
                nh = sum(1 for _, _, l in work.headings if rx.search(l))
                nb, shown = 0, 0
                for f in work.files:
                    for ln, l in enumerate(work.lines[f], 1):
                        if rx.search(l):
                            nb += 1
                            if not HEADING_RE.match(l) and shown < BODY_HITS_PER_TERM:
                                x["body_hits"].append({"term": t, "file": f, "line": ln})
                                shown += 1
                x["term_counts"][t] = [nh, nb]
            classify(x, work)
            out.append(x)
    return out, failures


def classify(x, work):
    cited = [o for o in x["official"] if o["cited_by"]]
    if cited:
        if any(o["after"] and o["section_level"] for o in cited):
            x["class"] = "strong_after_release"
        elif any(o["anchor"] and o["http"] == "200" and not o["section_level"] for o in cited):
            x["class"] = "strong_nosection"
        else:
            x["class"] = "strong"
    elif x["heading_hits"]:
        x["class"] = "heading_only"
    else:
        x["class"] = "none"
    x["cited_files"] = sorted({f for o in cited for f, _ in o["cited_by"]})
    x["candidates"] = sorted(set(x["cited_files"]) | {h["file"] for h in x["heading_hits"]})
    x["body_count"] = sum(nb for _, nb in x["term_counts"].values())
    x["sections"] = [re.sub(r'\s+', ' ', o["section_text"]) for o in cited if o["section_text"]]
    # 無い語: 節の強調語のうち、そのページを引用しているファイル（起点か作業ツリー）の作業ツリーの本文に
    # 部分一致で無いもの（大文字小文字を区別しない）。節が無ければ計算しない（0個）
    missing = []
    for o in cited:
        if not (o["anchor"] and o["section_level"]):
            continue
        files = sorted({f for f, _ in o["cited_by"]})
        txt = "".join(read(None, f) or "" for f in files).lower()
        missing += [t for t in o["section_terms"] if t.lower() not in txt and t not in missing]
    x["missing"] = missing


# ------------------------------------------------------------
# T1 の出力
# ------------------------------------------------------------
def cell(s):
    return s.replace("|", "\\|")


def item_label(x):
    return x["title"] or (x["body"][:60] + "…" if len(x["body"]) > 60 else x["body"])


def group_lines(pairs):
    by = collections.OrderedDict()
    for f, ln in pairs:
        by.setdefault(short(f), [])
        if ln not in by[short(f)]:
            by[short(f)].append(ln)
    return [f"{f}:{','.join(str(l) for l in sorted(ls))}" for f, ls in by.items()]


def official_cell(o):
    if o["http"] != "200":
        note = f"取得失敗（HTTP {o['http']}）"
    else:
        note = o["updated"] or "更新日なし"
        if o["anchor"] and not o["section_level"]:
            note += f"・⚠ 節が見つからない（id={o['anchor']}）"
    return f"`{o['href']}`（{note}）"


TABLE_HEADER = ("| ID | changelog 項目 | 公式の節（更新日） | 本サイトの候補（公式 URL を引用） "
                "| 本サイトの候補（見出し） | 検索語と件数（見出し/本文） | 本文の当たり（語ごとに先頭5件） "
                "| 公式の節にあって引用ページに無い語 | 区分 | 対応 |")


def render_table(items):
    out = [TABLE_HEADER, "|" + "---|" * 10]
    for x in items:
        off = "<br>".join(official_cell(o) for o in x["official"]) or "—"
        cites = "<br>".join(group_lines(c for o in x["official"] for c in o["cited_by"])) or "—"
        hd = group_lines((h["file"], h["line"]) for h in x["heading_hits"])
        heads = "<br>".join(hd[:HEADING_FILES_MAX]) + (
            f"<br>ほか{len(hd) - HEADING_FILES_MAX}ファイル" if len(hd) > HEADING_FILES_MAX else "")
        counts = "・".join(f"`{t}` {a}/{b}" for t, (a, b) in x["term_counts"].items()) or "—"
        body = "—"
        if x["class"] == "none" and x["body_count"]:
            by = collections.OrderedDict()
            for h in x["body_hits"]:
                by.setdefault(h["term"], []).append(f"{short(h['file'])}:{h['line']}")
            body = "<br>".join(f"`{t}` {', '.join(ls)}" for t, ls in by.items())
        miss = "・".join(f"`{m}`" for m in x["missing"]) or "—"
        out.append("| " + " | ".join(cell(c) for c in [
            x["id"], item_label(x), off, cites, heads or "—", counts, body, miss,
            CLASS_LABEL[x["class"]]]) + " |  |")
    return "\n".join(out)


def render_excerpts(items):
    seen = collections.OrderedDict()
    for x in items:
        for o in x["official"]:
            if o["section_text"]:
                key = o["href"]
                if key not in seen:
                    seen[key] = (o, [])
                seen[key][1].append(x["id"])
    if not seen:
        return ""
    chars = sum(len(o["section_text"]) for o, _ in seen.values())
    out = [f"<details><summary>公式の節の抜粋（{len(seen)}節・{chars:,}字）</summary>", ""]
    for o, ids in seen.values():
        out.append(f"#### {'・'.join(ids)} `{o['href']}`（h{o['section_level']}・{o['updated'] or '更新日なし'}）")
        out.append(o["section_text"])
        out.append("")
    out.append("</details>")
    return "\n".join(out)


def to_json(base_name, B, versions, items):
    keep = ("id", "version", "release_date", "source", "title", "body", "terms", "term_counts",
            "heading_hits", "body_hits", "missing", "class", "cited_files", "candidates")
    rows = []
    for x in items:
        r = {k: x[k] for k in keep}
        r["official"] = [{
            "href": o["href"], "http": o["http"], "updated": o["updated"], "after_release": o["after"],
            "section_found": bool(o["section_level"]), "section_level": o["section_level"],
            "cited_by": [{"file": f, "line": ln} for f, ln in o["cited_by"]],
        } for o in x["official"]]
        rows.append(r)
    return {"schema": 1, "base": base_name, "merge_base": B, "versions": versions, "items": rows}


def cmd_table(a):
    check_html_dir(a.html_dir)
    if a.versions:
        check_versions_arg(a.versions)
    B = merge_base(a.base)
    wanted = target_versions(B, a.versions)
    if wanted is None:
        print(NOT_UPDATE_MSG)
        return 0
    rel = load_releases(a.html_dir)
    versions = resolve_versions(wanted, rel)
    pages = OfficialPages()
    try:
        items, failures = analyze(B, versions, rel, pages)
    finally:
        pages.close()
    for x in items:
        for o in x["official"]:
            if o["http"] == "200" and o["anchor"] and not o["section_level"]:
                print(f"⚠ {DOCS_ORIGIN_DEFAULT}{o['path']} に id {o['anchor']} がありません", file=sys.stderr)
    print(f"起点（merge-base）: {B[:7]}（BASE {a.base}）/ 版: {', '.join(versions)} / 項目 {len(items)}")
    print("")
    print(render_table(items))
    print("")
    print(f"**§6.4 の同期対象（項目に関係なく確かめる）**: {'・'.join(SYNC_TARGETS)}"
          f"・`.github/release-notes/v{max(versions, key=ex.version_key)}.md`")
    if not a.no_excerpts:
        exc = render_excerpts(items)
        if exc:
            print("")
            print(exc)
    if a.json:
        try:
            with open(a.json, "w", encoding="utf-8") as f:
                json.dump(to_json(a.base, B, versions, items), f, ensure_ascii=False, indent=1)
        except OSError as e:
            raise Fail(2, f"--json に書けません: {a.json}（{e.strerror}）")
    seen = set()
    for p in failures:
        if p["url"] not in seen:
            seen.add(p["url"])
            print(f"⚠ 取得失敗: {p['url']} HTTP {p['http']}")
    return 3 if failures else 0


# ------------------------------------------------------------
# T3 削除された記述
# ------------------------------------------------------------
def md_cells(l):
    return [c.strip() for c in l.strip().strip("|").split("|")]


def md_plain(c):
    return re.sub(r'\s+', ' ', re.sub(r'(\*\*|`|\[|\]\([^)]*\))', '', c)).strip()


NUM_RE = re.compile(r'\d+(?:\.\d+)*')


def normnum(s):
    return NUM_RE.sub("#", s)


def md_tables(txt):
    """[(直前の見出し, 開始行, 列名, [(行番号, セル)])]。コードフェンスの中は除く。"""
    L = txt.split("\n")
    out, head, i, fence = [], None, 0, False
    while i < len(L):
        if L[i].lstrip().startswith("```"):
            fence = not fence
            i += 1
            continue
        if fence:
            i += 1
            continue
        if re.match(r'#+ ', L[i]):
            head = L[i].strip()
        if L[i].lstrip().startswith("|") and i + 1 < len(L) and re.match(r'^\s*\|?\s*:?-{3,}', L[i + 1]):
            hdr = [md_plain(c) for c in md_cells(L[i])]
            rows, j = [], i + 2
            while j < len(L) and L[j].lstrip().startswith("|"):
                rows.append((j + 1, [md_plain(c) for c in md_cells(L[j])]))
                j += 1
            out.append((head, i + 1, hdr, rows))
            i = j
            continue
        i += 1
    return out


def md_sentences(txt):
    out, fence = [], False
    for n, l in enumerate(txt.split("\n"), 1):
        s = l.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence or not s or s.startswith("|") or re.match(r'^(#+ |<a id=|---$)', s):
            continue
        for p in re.split(r'(?<=。)', s):
            p = p.strip()
            if len(md_plain(p)) >= 8:
                out.append((n, p))
    return out


def removed(B, head=None):
    """起点 B と作業ツリー（head を渡せばその木）を比べる。

    返り値: (判断が要る項目 [(file, line, kind, text)], 判断不要の項目, 対象ファイル)。
    kind は 表ごと消えた・列が消えた・消えた行（判断が要る）、書き換えた行・消えた文（判断不要）。
    """
    names = git("diff", "--name-only", B, *([head] if head else []), "--", *SCOPE).split("\n")
    fs = [f for f in names if f.endswith(".md")]
    need, info = [], []
    for f in fs:
        b = read(B, f) or ""
        h = read(head, f)
        if h is None:
            need.append((f, 1, "表ごと消えた", "ファイルが削除された"))
            continue
        bt, ht = md_tables(b), md_tables(h)
        by_head = collections.defaultdict(list)
        for t in ht:
            by_head[t[0]].append(t)
        used, unmatched = collections.Counter(), list(ht)
        for sec, ln, hdr, rows in bt:
            k = used[sec]
            used[sec] += 1
            cand = by_head.get(sec, [])
            match = cand[k] if k < len(cand) else None
            if match is None:   # 見出しが変わった表: 列名の一致が最も多い未対応の表
                best = max(unmatched, key=lambda t: len(set(t[2]) & set(hdr)), default=None)
                match = best if best and set(best[2]) & set(hdr) else None
            if match is None:
                need.append((f, ln, "表ごと消えた", f"（{sec}）列 {hdr}、{len(rows)} 行"))
                continue
            if match in unmatched:
                unmatched.remove(match)
            _, _, hhdr, hrows = match
            for c in [c for c in hdr if c not in hhdr]:
                need.append((f, ln, "列が消えた", f"「{c}」（{sec}）"))
            common = [c for c in hdr if c in hhdr]
            bi = [hdr.index(c) for c in common]
            hi = [hhdr.index(c) for c in common]
            hp = collections.Counter(tuple(r[i] if i < len(r) else "" for i in hi) for _, r in hrows)
            hcells = [set(r[i] if i < len(r) else "" for _, r in hrows) for i in hi]
            for rln, r in rows:
                p = tuple(r[i] if i < len(r) else "" for i in bi)
                if hp[p] > 0:
                    hp[p] -= 1
                    continue
                if tuple(normnum(x) for x in p) in {tuple(normnum(x) for x in q) for q in hp}:
                    continue
                # 値が数字だけのセルは「同じ値」に数えない（番号の列だけで「書き換えた行」にしない）
                same = [common[k] for k, x in enumerate(p)
                        if x and not re.fullmatch(r'[\d.]+', x) and x in hcells[k]]
                row = "| " + " | ".join(r) + " |"
                if same:
                    info.append((f, rln, "書き換えた行", row + f"（同じ値の列: {'・'.join(same)}）"))
                else:
                    need.append((f, rln, "消えた行", row))
        hn = md_plain(h)
        hnn = normnum(hn)
        for n, s in md_sentences(b):
            ps = md_plain(s)
            if ps in hn or normnum(ps) in hnn:
                continue
            info.append((f, n, "消えた文", s))
    return need, info, fs


def render_removed(need, info):
    out = [f"- {short(f)} L{n} {k}: {t} 判断: " for f, n, k, t in need]
    if info:
        out.append("<details><summary>判断不要（書き換えた行・消えた文）</summary>\n")
        out += [f"- {short(f)} L{n} {k}: {t}" for f, n, k, t in info]
        out.append("</details>")
    return "\n".join(out) if out else "削除された記述はありません"


def cmd_removed(a):
    if a.head and resolve_commit(a.head) is None:
        raise Fail(2, f"--head を解決できません: {a.head}")
    B = merge_base(a.base)
    need, info, fs = removed(B, a.head)
    print(render_removed(need, info))
    print(f"# 起点（merge-base）: {B[:7]}（BASE {a.base}）/ 対象 {len(fs)} ファイル / "
          f"判断が要る {len(need)} / 判断不要 {len(info)}", file=sys.stderr)
    return 0


# ------------------------------------------------------------
# 公式の節の切り出し（手順書 §6.6.3）
# ------------------------------------------------------------
def cmd_section(a):
    if not a.url.startswith("https://kiro.dev/"):
        raise Fail(2, f"--url は https://kiro.dev/ で始まる URL にしてください: {a.url}")
    if not SECTION_ID_RE.match(a.id):
        raise Fail(2, f"--id の形式が違います（[a-z0-9-]）: {a.id}")
    path = norm_path(a.url[len("https://kiro.dev"):])
    pages = OfficialPages()
    try:
        page = pages.get(path)
    finally:
        pages.close()
    if page["html"] is None:
        raise Fail(3, f"取得失敗: {page['url']} HTTP {page['http']}")
    updated = page_updated(page["html"]) or "更新日なし"
    _, hs = heading_ids(page["html"])
    if not a.id:
        print(f"Page updated: {updated}")
        print("\n".join(f"h{l} {i}" for _, l, i in hs))
        return 0
    lvl, frag = section_html(page["html"], a.id)
    if lvl is None:
        print(f"❌ id {a.id} がありません。--id '' で h2〜h4 の id の一覧を出してください")
        return 1
    print(f"h{lvl} {a.id}（Page updated: {updated}）")
    print(fragment_text(frag))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("table", help="T1: 対応表の雛形")
    t.add_argument("--html-dir", required=True, help="取得済み changelog HTML のディレクトリ")
    t.add_argument("--versions", help="版（カンマ区切り）。無ければ changelog の目次の差")
    t.add_argument("--base", default=DEFAULT_BASE, help=f"起点を決める BASE（既定 {DEFAULT_BASE}）")
    t.add_argument("--json", help="機械可読の出力先")
    t.add_argument("--no-excerpts", action="store_true", help="公式の節の抜粋を出さない")
    r = sub.add_parser("removed", help="T3: 削除された記述")
    r.add_argument("--base", default=DEFAULT_BASE)
    r.add_argument("--head", help="比べる木（既定は作業ツリー）")
    s = sub.add_parser("section", help="公式の節の切り出し")
    s.add_argument("--url", required=True)
    s.add_argument("--id", required=True, help="見出しの id。空なら id の一覧")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    os.chdir(repo_root())
    try:
        return {"table": cmd_table, "removed": cmd_removed, "section": cmd_section}[a.cmd](a)
    except Fail as e:
        return report(e)
    except Exception as e:
        print(f"⚠ 予期しない例外: {type(e).__name__}: {e}（未検証）")
        return 3


if __name__ == "__main__":
    sys.exit(main())
