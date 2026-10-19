#!/usr/bin/env python3
"""reel1 (@englishwithkursat): one 14s Turkish take about writing, bold look throughout.
Built from the /video-edit template: dude_words(), grades(), audio(), SAFE_GUIDE and the cut times are its machinery;
GROUPS and SFX are this reel's content. Unused template parts (cards, cool girl, orbit, cool dude, inserts) removed.

Segments (segments.json): hook 0-3.70 wide | s2 punch-in 1.2x | s3 wide.
Word times: words.json (large-v3, Turkish) runs ~0.15s early here, so the times below are words.json + .15,
checked against silencedetect phrase starts (3.75, 6.26, 7.03, 8.18, 10.55).

Run from the project folder with PY, the skill's Python (see SKILL.md):
PY build.py            writes index.html
PY build.py --safe     same + red Instagram safe-zone guide (snapshots only, never render with it)
"""
import json
import os
import shutil
import subprocess
import sys

SAFE = '--safe' in sys.argv or bool(os.environ.get('SAFE'))
DUR = float(subprocess.run([shutil.which('ffprobe') or 'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=duration', '-of', 'csv=p=0', 'assets/aroll.mp4'],
                           capture_output=True, encoding='utf-8', errors='replace').stdout.strip().split(',')[0])
YEL = '#FAE67A'
with open('segments.json', encoding='utf-8') as _f:
    SEG = {s['id']: s for s in json.load(_f)}
# cut times = exact first frame of each segment, nudged 2ms early so a tl.set lands ON that frame
T = {k: s['frame'] / 30 - .002 if s['frame'] else 0.0 for k, s in SEG.items()}
CUTS = [T['s2'], T['s3']]

BOLD_F = 'contrast(1.07) saturate(.9) brightness(.97)'

# Instagram Reels safe zone: top 220, bottom 450 (nothing below y=1470), sides 35, right 100 from y~1155.
# Behind-head words: top = head_top + .15*S - .72*S (layout.md). Head tops from headpos.py: hook 324, s2 352, s3 304.
C = 'left:0;right:0;text-align:center;'
LO1, LO2 = C + 'top:1010px', C + 'top:1100px'
PUNCH = C + 'top:1110px'
GROUPS = [  # (start, end, [(t, text, classes, style)])
    (0.00, 1.20, [(0.00, 'kafanda çok iyi', 'sm', LO1), (0.78, 'konuşuyorsun', 'sm', LO2)]),
    (1.20, 2.35, [(1.22, 'ama cümle', 'sm', LO1), (1.70, 'kurmaya gelince', 'sm', LO2)]),
    (2.35, CUTS[0], [(2.37, 'her şeyin yeri', 'sm', LO1), (3.15, 'karışıyor.', 'md y', C + 'top:224px')]),
    (CUTS[0], 5.05, [(3.75, 'neyse', 'sm', LO1), (4.05, 'kimsenin konuşmadığı', 'sm', LO2)]),
    (5.05, 6.20, [(5.05, 'harika bir', 'sm', LO1), (5.47, 'çözüm var.', 'md y', PUNCH)]),
    (6.20, CUTS[1], [(6.24, 'writing.', 'xl back y', C + 'top:227px')]),
    (CUTS[1], 8.12, [(7.03, 'iyi de', 'sm', LO1), (7.50, 'ne alaka?', 'md y', PUNCH)]),
    (8.12, 9.40, [(8.18, 'dört', 'md y', C + 'top:950px'), (8.55, 'önemli nedeni var', 'sm', C + 'top:1110px')]),
    (9.40, 10.50, [(9.45, 've sonuncusu', 'sm', LO1), (9.85, 'en önemlisi.', 'md y', PUNCH)]),
    (10.50, 11.80, [(10.55, 'yazı yazarken', 'sm', LO1), (11.19, 'acele etmeden', 'sm', LO2)]),
    (11.80, 12.72, [(11.83, 'kafanda', 'sm', LO1), (12.23, 'kurabilirsin.', 'sm y', LO2)]),
    (12.72, DUR, [(12.77, 'karşında seni', 'sm', LO1), (13.25, 'bekleyen yok.', 'sm y', LO2)]),
]


def dude_words():
    html, tw = [], []
    for g, (a, b, words) in enumerate(GROUPS):
        for k, (t, txt, cls, st) in enumerate(words):
            wid = f'w{g}-{k}'
            html.append(f'<div id="{wid}" class="dw {cls}" style="{st}">{txt}</div>')
            tw.append(f"gsap.set('#{wid}',{{autoAlpha:0}});")
            tw.append(f"tl.fromTo('#{wid}',{{autoAlpha:0,scale:1.22,filter:'blur(22px)'}},{{autoAlpha:1,scale:1,filter:'blur(0px)',"
                      f"duration:.2,ease:'power3.out',immediateRender:false}},{max(a, t - .05):.3f});")
            if b < DUR - .01:
                tw.append(f"tl.to('#{wid}',{{autoAlpha:0,scale:.96,filter:'blur(16px)',duration:.12,ease:'power2.in'}},{b - .12:.3f});")
                tw.append(f"tl.set('#{wid}',{{autoAlpha:0}},{b:.3f});")
    return html, tw


def grades():
    tw = [f"gsap.set('.g',{{filter:'{BOLD_F}'}});"]
    for t in CUTS:
        tw.append(f"tl.fromTo('#stage',{{scale:1.05}},{{scale:1,duration:.32,ease:'power2.out',immediateRender:false}},{t:.3f});")
    return tw


SFX = [('whoosh-short', .12, .25), ('whoosh-short', CUTS[0] - .1, .22), ('whoosh-short', CUTS[1] - .1, .22),
       ('pop', 5.47, .18), ('pop', 7.50, .18), ('pop', 9.85, .18)]
SFX_LEN = {'whoosh-short': .57, 'pop': .72, 'sparkle': 1.8, 'click': .3, 'click-soft': .37}
SFX_GAIN = 0.75   # sounds sit 25% under the original levels: subtle, never louder than the voice


def audio():
    out, lanes = [], []
    for k, (name, t, vol) in enumerate(sorted(SFX, key=lambda x: x[1])):
        d = min(SFX_LEN[name], DUR - t)
        lane = next((i for i, end in enumerate(lanes) if end <= t), None)
        if lane is None:
            lanes.append(0); lane = len(lanes) - 1
        lanes[lane] = t + d
        out.append(f'<audio id="sfx{k}" src="assets/sfx/{name}.mp3" data-start="{t:.3f}" data-duration="{d:.3f}" '
                   f'data-track-index="{10 + lane}" data-volume="{vol * SFX_GAIN:.3f}"></audio>')
    return out


CSS = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
#stage{{position:absolute;inset:0;transform-origin:50% 45%}}
.full{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#bgv{{z-index:0}}
.dw.back{{z-index:3}}
#cutwrap{{position:absolute;inset:0;z-index:4}}

/* look overlays */
.fx{{position:absolute;inset:0;pointer-events:none}}
#dtone{{z-index:7;background:linear-gradient(180deg,rgba(20,55,75,.16),rgba(60,40,20,.08));mix-blend-mode:soft-light}}
#dvig{{z-index:7;background:radial-gradient(95% 62% at 50% 46%,rgba(0,0,0,0) 55%,rgba(0,0,0,.42) 100%)}}
#dgrad{{z-index:7;background:linear-gradient(180deg,rgba(0,0,0,.34) 0%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 58%,rgba(0,0,0,.30) 100%)}}

/* base type */
.dw{{position:absolute;z-index:8;color:#fff;font-family:'Inter Tight';font-weight:900;letter-spacing:-.05em;line-height:.9;
  text-shadow:0 10px 40px rgba(0,0,0,.55),0 2px 8px rgba(0,0,0,.35);transform-origin:50% 60%;white-space:nowrap}}
.sm{{font-size:84px;font-weight:800;letter-spacing:-.04em}}
.sm2{{font-size:56px;font-weight:800;letter-spacing:-.03em}}
.md{{font-size:150px}}
.big{{font-size:236px}}
.xl{{font-size:220px}}
.huge{{font-size:300px}}
.y{{color:{YEL}}}
'''


# PY build.py --safe: draws the Instagram safe zone (red = UI covers it) for snapshot checks, never for renders
SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>')


def build():
    w_html, w_tw = dude_words()
    back = [h for h in w_html if 'back' in h.split('class="')[1].split('"')[0]]
    front = [h for h in w_html if h not in back]
    tweens = grades() + w_tw
    nl = '\n'
    # gsap served locally (assets/gsap.min.js, from npm): this environment's network blocks cdn.jsdelivr.net
    return f'''<!doctype html>
<html lang="tr" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<link rel="stylesheet" href="assets/fonts/fonts.css" />
<script src="assets/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="1080" data-height="1920">
  <audio id="bga" src="assets/aroll.mp4" data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="2" data-volume="1"></audio>
{nl.join(audio())}
  <div id="stage">
    <video id="bgv" class="full g" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="0"></video>
{nl.join(back)}
    <div id="cutwrap"><video id="cut" class="full g" src="assets/subject.webm" muted playsinline data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="1"></video></div>
  </div>
  <div id="dtone" class="fx"></div><div id="dvig" class="fx"></div><div id="dgrad" class="fx"></div>
{nl.join(front)}
{SAFE_GUIDE if SAFE else ''}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{nl.join(tweens)}
tl.set({{}}, {{}}, {DUR:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''


# utf-8 on every OS: the page declares charset UTF-8, and Windows would otherwise write cp1252 (broken accents, emoji)
with open('index.html', 'w', encoding='utf-8', newline='\n') as _f:
    _f.write(build())
print(f'wrote index.html {DUR:.3f}s  cuts {[round(c, 3) for c in CUTS]}')
