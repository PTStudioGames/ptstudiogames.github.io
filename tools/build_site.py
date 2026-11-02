import html, re, shutil, subprocess, sys
from pathlib import Path
SRC = Path(__file__).resolve().parents[2] / "blender-addons" / "products"
OUT = Path(sys.argv[1])
ORDER = ["shotlist"]

def sections(md):
    out, cur = {}, None
    for line in md.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip(); out[cur] = []
        elif cur:
            out[cur].append(line)
    return out

def field(md, name):
    m = re.search(rf"\*\*{name}:\*\*\s*(.+)", md)
    return m.group(1).strip() if m else ""

def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)

def bullets(lines):
    items = []
    for l in lines:
        if l.startswith("- "): items.append(l[2:].strip())
        elif l.startswith("  ") and items: items[-1] += " " + l.strip()
    return items

def para(lines):
    return " ".join(l.strip() for l in lines if l.strip())

(OUT / "img").mkdir(parents=True, exist_ok=True)
cards, blocks = [], []
for p in ORDER:
    md = (SRC / p / "listing" / "superhive.md").read_text()
    s = sections(md)
    name = field(md, "Product name").split(" — ")[0]
    tag = field(md, "Tagline")
    hero = OUT / "img" / f"{p}-hero.jpg"
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", "-Z", "1600",
                    str(SRC / p / "listing/images/hero.png"), "--out", str(hero)], check=True, capture_output=True)
    shutil.copy(SRC / p / "listing/demo.mp4", OUT / "img" / f"{p}-demo.mp4")
    feats = "".join(f"<li>{inline(f)}</li>" for f in bullets(s.get("Features", [])))
    cards.append(f'<a class="card" href="#{p}"><img src="img/{p}-hero.jpg" alt="{html.escape(name)}" loading="lazy">'
                 f'<h3>{html.escape(name)}</h3><p>{inline(tag)}</p></a>')
    blocks.append(f'''<section class="addon" id="{p}">
  <h2>{html.escape(name)}</h2>
  <p class="tag">{inline(tag)}</p>
  <video src="img/{p}-demo.mp4" poster="img/{p}-hero.jpg" autoplay muted loop playsinline controls></video>
  <p>{inline(para(s.get("Pitch", [])))}</p>
  <h4>The problem it solves</h4>
  <p>{inline(para(s.get("The problem it solves", [])))}</p>
  <h4>Features</h4>
  <ul>{feats}</ul>
  <p class="meta">Blender 4.2 and later · Eevee and Cycles · Coming soon to Superhive</p>
</section>''')

page = (Path(__file__).parent / "template.html").read_text()
page = page.replace("{{CARDS}}", "\n".join(cards)).replace("{{BLOCKS}}", "\n".join(blocks))
(OUT / "index.html").write_text(page)
print("ok", OUT)
