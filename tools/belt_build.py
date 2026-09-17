# -*- coding: utf-8 -*-
"""AI 사범님 데이터 → 홈페이지에 반영.

    index.html   「띠 승급 체계」 섹션 (BELT:START ~ BELT:END)
    catalog.html  띠별 교육과정 카탈로그
    consult.html  입관 상담 페이지의 승급 데이터

사용법:  python tools/belt_build.py
원본(AI 사범님 폴더)은 읽기만 한다. 학생 인원 수는 공개 페이지에 싣지 않고,
프로그램에 저장된 휴대폰 번호는 대표번호로 바꿔 싣는다.
"""
import html, io, json, os, re, sys

APP_SRC = os.environ.get('AI_SABUM_SRC', r'D:/ai 사범님/src')
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_TEL = '0507-1307-7239'
MOBILE = re.compile(r'01[016789]-?\d{3,4}-?\d{4}')
BASE = 'https://moneystar4326-byte.github.io/gangdam-taekwondo/'

os.chdir(APP_SRC)
sys.path.insert(0, APP_SRC)
sys.argv = ['app.py']
import app, catalog, curriculum, character, store  # noqa: E402

raw = store.read_dojang()
cur = store.read_curriculum()
rows = curriculum.own_ranks(raw.get('ranks', []), cur.get('_upto', ''))
ch = character.normalize(store.read_character())
d = app._dojang()
for k in ('intro', 'tel', 'address'):
    setattr(d, k, raw.get(k, ''))
data = catalog.collect(d, cur, ch, raw.get('ranks', []), rows, {}, app._areas())
steps = data['steps']
e = lambda s: html.escape(str(s or ''))


# ---------------------------------------------------------------- catalog.html
body = catalog.build_html(data)
body = MOBILE.sub(PUBLIC_TEL, body)
body = re.sub(r'<div class="printbar">.*?</div>\s*', '', body, count=1, flags=re.S)
body = re.sub(r'(?is)^\s*<!doctype[^>]*>', '', body)
body = re.sub(r'(?is)</?(html|body)[^>]*>', '', body)
head_extra = ''
m = re.search(r'(?is)<head[^>]*>(.*?)</head>', body)
if m:
    head_extra = m.group(1)
    body = body[:m.start()] + body[m.end():]
head_extra = re.sub(r'(?is)<title>.*?</title>|<meta[^>]*charset[^>]*>|<meta[^>]*viewport[^>]*>', '', head_extra)

page = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>띠별 교육과정 | 용인대석사 강담태권도</title>
<meta name="description" content="강담태권도의 흰띠부터 4품까지 띠별 교육과정과 연간 인성교육 안내입니다.">
<link rel="canonical" href="{BASE}catalog.html">
<link rel="icon" href="assets/img/logo-mark.png">
{head_extra}
<style>
.sitebar{{position:sticky;top:0;z-index:50;display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:10px 18px;background:#0B1B3A;color:#fff;font:600 14px/1.4 "Pretendard","Noto Sans KR",sans-serif}}
.sitebar a{{color:#fff;text-decoration:none;display:inline-flex;align-items:center;gap:8px}}
.sitebar img{{height:28px;width:auto;background:#fff;border-radius:50%;padding:3px}}
.sitebar button{{font:inherit;color:#0B1B3A;background:#E9B949;border:0;border-radius:999px;padding:7px 16px;cursor:pointer}}
@media print{{.sitebar{{display:none}}}}
</style>
</head>
<body>
<div class="sitebar">
  <a href="./"><img src="assets/img/logo-mark.png" alt="">← 강담태권도 홈페이지</a>
  <button type="button" onclick="window.print()">인쇄하기</button>
</div>
{body}
</body>
</html>
'''
io.open(os.path.join(SITE, 'catalog.html'), 'w', encoding='utf-8').write(page)


# ------------------------------------------------------- index.html 섹션
def row(s):
    ranks = [r for r in s['ranks'] if r != s['name']]
    meta = ' · '.join(ranks + ['%d개월' % s['months']])
    # 세로 막대에서는 반반 띠가 위아래로 보여야 한다
    cord = s['style'].replace('90deg', '180deg')
    tags = ''.join(f'<span>{e(x)}</span>' for x in (s.get('learn') or []))
    light = ' belt__cord--light' if '#F4F4F2' in s['style'] else ''
    return f'''      <li class="belt" data-reveal>
        <span class="belt__cord{light}" style="{e(cord)}" aria-hidden="true"></span>
        <div class="belt__head">
          <b>{e(s['name'])}</b>
          <span>{e(meta)}</span>
        </div>
        <div class="belt__body">
          <p>{e(s['parent'])}</p>
          <div class="belt__tags">{tags}</div>
        </div>
      </li>'''

kup = [s for s in steps if '품' not in s['name']]
poom = [s for s in steps if '품' in s['name']]
strip = ''.join(f'<span style="{e(s["style"])}"></span>' for s in steps)
virtues = ' · '.join(e(m.get('virtue')) for m in data['months'])

section = f'''<!-- BELT:START — belt_build.py 가 AI 사범님 데이터로 생성합니다. 직접 고치지 마세요. -->
<section class="section" id="belt">
  <div class="container">
    <div class="section-head center" data-reveal>
      <span class="eyebrow">BELT SYSTEM</span>
      <h2 class="title">흰띠에서 검은띠까지,<br><span class="hl">아이가 걸어갈 길</span></h2>
      <p class="lead">띠는 색만 바뀌는 게 아닙니다. 띠마다 무엇을 얼마 동안 가르칠지 미리 정해 두고 그대로 갑니다. 흰띠에서 빨간띠까지 약 1년입니다.</p>
    </div>

    <div class="belt-strip" aria-hidden="true">{strip}</div>

    <h3 class="belt-group">급 과정 <small>흰띠 → 국기원반</small></h3>
    <ol class="belts">
{chr(10).join(row(s) for s in kup)}
    </ol>

    <p class="belt-knot"><span>여기서부터 국기원 승품 심사</span></p>

    <h3 class="belt-group">품 과정 <small>1품 → 4품</small></h3>
    <ol class="belts">
{chr(10).join(row(s) for s in poom)}
    </ol>

    <div class="belt-foot" data-reveal>
      <p>모든 띠에서 <b>인성교육 12가지</b>를 한 달에 하나씩 함께 배웁니다 — {virtues}</p>
      <a href="catalog.html" class="btn btn--primary">
        띠별 교육과정 전체 보기
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
      </a>
    </div>
  </div>
</section>
<!-- BELT:END -->
'''

p = os.path.join(SITE, 'index.html')
s = io.open(p, encoding='utf-8').read()
if '<!-- BELT:START' in s:
    s = re.sub(r'<!-- BELT:START.*?<!-- BELT:END -->\n', lambda _: section, s, flags=re.S)
else:
    anchor = '<!-- ================= SCHEDULE ================= -->'
    assert anchor in s
    s = s.replace(anchor, section + '\n' + anchor, 1)
if 'href="#belt"' not in s:
    s = s.replace('<a href="#program">프로그램</a>',
                  '<a href="#program">프로그램</a>\n      <a href="#belt">승급체계</a>', 1)
io.open(p, 'w', encoding='utf-8').write(s)

# ------------------------------------------------------- consult.html 데이터
def cord(style):
    return style.replace('90deg', '180deg')

payload = {
    'steps': [{'name': x['name'], 'ranks': x['ranks'], 'months': x['months'], 'cord': cord(x['style'])}
              for x in steps],
    'virtues': [{'no': m['no'], 'virtue': m.get('virtue', '')} for m in data['months']],
}
cp = os.path.join(SITE, 'consult.html')
if os.path.exists(cp):
    c = io.open(cp, encoding='utf-8').read()
    blob = json.dumps(payload, ensure_ascii=False).replace('</', r'<\/')
    c, n = re.subn(r'(<script id="belt-data" type="application/json">).*?(</script>)',
                   lambda mm: mm.group(1) + blob + mm.group(2), c, count=1, flags=re.S)
    assert n == 1, 'consult.html 에 belt-data 자리가 없습니다'
    io.open(cp, 'w', encoding='utf-8').write(c)

print('steps=%d (급 %d, 품 %d) virtues=%d' % (len(steps), len(kup), len(poom), len(data['months'])))
print('catalog.html %d KB, 휴대폰 번호 잔존=%d, consult 데이터=%d단계' % (
    len(page.encode()) // 1024, len(MOBILE.findall(page)), len(payload['steps'])))
