# -*- coding: utf-8 -*-
"""카드 5장 HTML 생성기. config의 스타일 토큰 사용. 빈 데이터는 블록 생략."""
from config import (
    BG, TXT, SUB, BLUE, GOLD, GREEN, RED, FRAME,
    CARD_W, CARD_H, SAFE_TOP, SAFE_BOTTOM,
)

BASE_CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:{CARD_W}px; height:{CARD_H}px; }}
body {{
  background:{BG};
  font-family:'Noto Sans CJK KR','Noto Sans CJK KR Black',sans-serif;
  color:{TXT}; overflow:hidden;
  word-break:keep-all; overflow-wrap:break-word;
}}
.headline,.why-heading,.sub,.why-body,.news-item {{ text-wrap:balance; }}
.card {{
  position:relative; width:{CARD_W}px; height:{CARD_H}px;
  padding:{SAFE_TOP}px 80px {SAFE_BOTTOM}px 80px;
  display:flex; flex-direction:column;
}}
.frame-top,.frame-bottom {{ position:absolute; left:80px; right:80px; height:2px; background:{FRAME}; }}
.frame-top {{ top:120px; }} .frame-bottom {{ bottom:120px; }}
.label {{ color:{BLUE}; font-weight:900; font-size:34px; letter-spacing:6px; margin-bottom:40px; }}
.headline {{ color:{TXT}; font-weight:900; font-size:96px; line-height:1.18; letter-spacing:-2px; }}
.headline .num {{ color:{GOLD}; }}
.sub {{ color:{SUB}; font-weight:700; font-size:40px; line-height:1.5; margin-top:48px; }}
.footer {{ position:absolute; left:80px; bottom:180px; color:{SUB}; font-weight:700; font-size:30px; letter-spacing:2px; }}
.section-title {{ color:{BLUE}; font-weight:900; font-size:54px; letter-spacing:2px; margin-bottom:64px; }}
.news-item {{ color:{TXT}; font-weight:700; font-size:46px; line-height:1.4; margin-bottom:56px; padding-left:36px; border-left:6px solid {BLUE}; }}
.bar-row {{ margin-top:20px; margin-bottom:44px; }}
.bar-label {{ color:{SUB}; font-weight:700; font-size:34px; margin-bottom:16px; }}
.bar-track {{ width:100%; height:44px; background:rgba(157,176,200,0.12); border-radius:4px; overflow:hidden; }}
.bar-fill {{ height:100%; background:{BLUE}; }}
.bar-fill.gold {{ background:{GOLD}; }}
.bar-val {{ color:{TXT}; font-weight:900; font-size:36px; margin-top:12px; }}
.stat {{ margin-bottom:88px; }}
.stat-num {{ font-weight:900; font-size:120px; line-height:1; color:{GOLD}; }}
.stat-num.blue {{ color:{BLUE}; }}
.stat-desc {{ color:{SUB}; font-weight:700; font-size:40px; margin-top:20px; }}
.why-heading {{ color:{TXT}; font-weight:900; font-size:64px; line-height:1.25; margin-bottom:56px; }}
.why-body {{ color:{SUB}; font-weight:700; font-size:44px; line-height:1.6; }}
.mkt-company {{ color:{SUB}; font-weight:700; font-size:44px; letter-spacing:2px; margin-bottom:24px; }}
.mkt-price {{ font-weight:900; font-size:150px; line-height:1; color:{TXT}; }}
.mkt-change {{ font-weight:900; font-size:64px; margin-top:24px; }}
.mkt-change.up {{ color:{GREEN}; }}
.mkt-change.down {{ color:{RED}; }}
.mkt-noprice {{ color:{SUB}; font-weight:900; font-size:60px; margin-top:24px; }}
.chart-wrap {{ margin-top:80px; }}
.note {{ color:{SUB}; font-weight:700; font-size:30px; line-height:1.5; margin-top:60px; }}
.source {{ color:{SUB}; font-weight:700; font-size:28px; margin-top:32px; opacity:0.7; }}
"""


def _frame():
    return '<div class="frame-top"></div><div class="frame-bottom"></div>'


def _esc(s):
    """헤드라인/서브의 <br>,<span>은 허용하되 나머지는 그대로. Claude가 이미 안전 태그만 넣음."""
    return s if s else ""


def card_cover(d):
    return f"""<div class="card">{_frame()}
  <div class="label">HOLLYWOOD INDUSTRY</div>
  <div class="headline">{_esc(d.get('headline',''))}</div>
  <div class="sub">{_esc(d.get('cover_sub',''))}</div>
  <div class="footer">HOLLYWOOD 산업 리포트 · {d.get('date','')}</div>
</div>"""


def card_industry(d):
    items = "".join(f'<div class="news-item">{_esc(x)}</div>' for x in d.get("industry_items", []))
    bars = ""
    for b in d.get("industry_bars", []) or []:
        try:
            pct = max(0, min(100, int(b.get("pct", 0))))
        except (ValueError, TypeError):
            pct = 0
        gold = " gold" if b.get("gold") else ""
        bars += f"""<div class="bar-row">
      <div class="bar-label">{_esc(b.get('label',''))}</div>
      <div class="bar-track"><div class="bar-fill{gold}" style="width:{pct}%"></div></div>
      <div class="bar-val">{_esc(b.get('val',''))}</div>
    </div>"""
    return f"""<div class="card">{_frame()}
  <div class="section-title">01. INDUSTRY NEWS</div>
  {items}
  {bars}
</div>"""


def card_numbers(d):
    stats_data = d.get("stats", []) or []
    if not stats_data:
        # 스탯이 없으면 이 카드는 산업 뉴스 보조 텍스트로 대체하지 않고 최소 안내
        inner = '<div class="why-body">기사에 명시된 수치가 없어 이 카드는 생략되었습니다.</div>'
    else:
        inner = ""
        for i, s in enumerate(stats_data[:3]):
            blue = " blue" if i == 1 else ""
            inner += f"""<div class="stat">
      <div class="stat-num{blue}">{_esc(s.get('num',''))}</div>
      <div class="stat-desc">{_esc(s.get('desc',''))}</div>
    </div>"""
    return f"""<div class="card">{_frame()}
  <div class="section-title">02. BY THE NUMBERS</div>
  {inner}
</div>"""


def card_why(d):
    return f"""<div class="card">{_frame()}
  <div class="section-title">03. WHY IT MATTERS</div>
  <div class="why-heading">{_esc(d.get('why_heading',''))}</div>
  <div class="why-body">{_esc(d.get('why_body',''))}</div>
</div>"""


def _sparkline(history, w=920, h=340):
    if not history or len(history) < 2:
        return ""
    lo, hi = min(history), max(history)
    rng = (hi - lo) or 1
    n = len(history)
    pts = []
    for i, v in enumerate(history):
        x = i / (n - 1) * w
        y = h - (v - lo) / rng * (h - 40) - 20
        pts.append(f"{x:.1f},{y:.1f}")
    poly = " ".join(pts)
    last_x, last_y = pts[-1].split(",")
    up = history[-1] >= history[0]
    col = GREEN if up else RED
    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <polyline points="{poly}" fill="none" stroke="{BLUE}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="{last_x}" cy="{last_y}" r="12" fill="{col}"/>
</svg>"""


def card_market(d):
    close = d.get("close")
    change = d.get("change")
    history = d.get("history", []) or []

    if close is not None:
        price_html = f'<div class="mkt-price">${float(close):.2f}</div>'
    else:
        price_html = '<div class="mkt-noprice">라이브 차트 확인 필요</div>'

    change_html = ""
    if change is not None:
        up = float(change) >= 0
        cls = "up" if up else "down"
        arrow = "\u25b2" if up else "\u25bc"
        change_html = f'<div class="mkt-change {cls}">{arrow} {abs(float(change)):.1f}%</div>'

    chart = _sparkline(history)
    chart_html = f'<div class="chart-wrap">{chart}</div>' if chart else ""

    return f"""<div class="card">{_frame()}
  <div class="section-title">04. MARKET CLOSE</div>
  <div class="mkt-company">{_esc(d.get('company',''))} · {_esc(d.get('ticker',''))}</div>
  {price_html}
  {change_html}
  {chart_html}
  <div class="note">{_esc(d.get('map_note',''))}</div>
  <div class="source">{_esc(d.get('source',''))} · 종가 기준 {d.get('date','')}</div>
</div>"""


CARD_FUNCS = [card_cover, card_industry, card_numbers, card_why, card_market]
CARD_NAMES = ["card_01_cover", "card_02_industry", "card_03_numbers", "card_04_why", "card_05_market"]


def build_all_html(data):
    htmls = []
    for fn in CARD_FUNCS:
        body = fn(data)
        html = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<style>{BASE_CSS}</style></head><body>{body}</body></html>"""
        htmls.append(html)
    return htmls
