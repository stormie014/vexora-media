#!/usr/bin/env python3
"""Vexora sample-ad builder.

Usage: python3 build_samples.py spec.json OUT_DIR
  spec.json  — written by the run (see spec-example.json)
  OUT_DIR    — usually vexora-media/s/<token>   (published on GitHub Pages)

Writes into OUT_DIR:
  feed.jpg, story.jpg          Instagram-style mockups shown to the client (email + page)
  feed-ad.jpg, story-ad.jpg    the clean creatives (what would actually run)
  index.html                   private sample page (noindex)
  email.html, email.txt        Day 0 email (HTML with images from the public page URL, plain-text alternative)
  preview.jpg                  side-by-side contact image for Sara's review
Needs: playwright (chromium), Pillow.
"""
import html, json, os, shutil, sys, colorsys
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, "..", "fonts"))
SITE = "https://stormie014.github.io/vexora-media"

CTA = {  # default button labels per action, Meta's own CTA wording
    "order": {"es": "Pedir ahora", "en": "Order now"},
    "book": {"es": "Reservar", "en": "Book now"},
    "call": {"es": "Llamar", "en": "Call now"},
    "quote": {"es": "Cotizar", "en": "Get quote"},
}
SPONSORED = {"es": "Publicidad", "en": "Sponsored", "both": "Sponsored"}
e = lambda s: html.escape(str(s or ""))


def t(spec, es, en):
    """Pick a string by the spec language; 'both' stacks them."""
    lang = spec.get("lang", "es")
    if lang == "en":
        return en
    if lang == "both":
        return f"{es} / {en}"
    return es


# ---------- colour ----------
def palette(photo_paths, override=None):
    if override and override.get("accent"):
        acc = override["accent"]
    else:
        acc = "#0D7C80"
        best = -1
        for p in photo_paths[:2]:
            try:
                im = Image.open(p).convert("RGB")
                im.thumbnail((160, 160))
                q = im.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
                pal = q.getpalette()[:24]
                counts = sorted(q.getcolors(), reverse=True)
                for n, idx in counts:
                    r, g, b = pal[idx * 3: idx * 3 + 3]
                    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
                    if 0.25 < l < 0.62 and s > 0.35:
                        score = s * (n ** 0.5)
                        if score > best:
                            best = score
                            acc = "#%02x%02x%02x" % (r, g, b)
            except Exception:
                pass
    r, g, b = (int(acc[i:i + 2], 16) for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    # keep the accent dark enough for white text (contrast)
    l = min(l, 0.42)
    ar, ag, ab = colorsys.hls_to_rgb(h, l, max(s, 0.45))
    accent = "#%02x%02x%02x" % (int(ar * 255), int(ag * 255), int(ab * 255))
    dr, dg, db = colorsys.hls_to_rgb(h, 0.12, min(0.5, s))
    deep = "#%02x%02x%02x" % (int(dr * 255), int(dg * 255), int(db * 255))
    lr, lg, lb = colorsys.hls_to_rgb(h, 0.93, min(0.6, s))
    light = "#%02x%02x%02x" % (int(lr * 255), int(lg * 255), int(lb * 255))
    return {"accent": accent, "deep": deep, "light": light}


def prep_photo(src, dst, size):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    im = ImageOps.fit(im, size, Image.LANCZOS, centering=(0.5, 0.45))
    im.save(dst, quality=90)
    return dst


# ---------- HTML ----------
def base_css(c):
    return f"""
@font-face{{font-family:D;src:url('file://{FONTS}/BricolageGrotesque.ttf')}}
@font-face{{font-family:B;src:url('file://{FONTS}/Figtree.ttf')}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#fff}}
:root{{--acc:{c['accent']};--deep:{c['deep']};--light:{c['light']}}}
"""


def creative_feed(spec, c, photo):
    a = spec["ad1"]
    bg = (f"<img class=ph src='file://{photo}'>" if photo else
          "<div class=pat></div>")
    return f"""<div class="cr feed {'nophoto' if not photo else ''}">
  {bg}<div class=shade></div>
  <div class=top><span class=brand>{e(spec['business'])}</span></div>
  <div class=bottom>
    {f"<span class=eyebrow>{e(a.get('eyebrow'))}</span>" if a.get('eyebrow') else ''}
    <h1>{e(a['headline'])}</h1>
    {f"<div class=offer>{e(a['offer'])}</div>" if a.get('offer') else ''}
  </div>
</div>"""


def creative_story(spec, c, photo):
    a = spec["ad2"]
    bg = (f"<img class=ph src='file://{photo}'>" if photo else "<div class=pat></div>")
    return f"""<div class="cr story {'nophoto' if not photo else ''}">
  {bg}<div class=shade></div>
  <div class=s-mid>
    {f"<span class=eyebrow>{e(a.get('eyebrow'))}</span>" if a.get('eyebrow') else ''}
    <h1>{e(a['headline'])}</h1>
    {f"<div class='offer tilt'>{e(a['offer'])}</div>" if a.get('offer') else ''}
  </div>
</div>"""


CR_CSS = """
.cr{position:relative;overflow:hidden;background:var(--deep);color:#fff;font-family:B}
.cr.feed{width:1080px;height:1350px}
.cr.story{width:1080px;height:1920px}
.ph{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.pat{position:absolute;inset:0;background:
  radial-gradient(circle at 85% 12%,var(--acc) 0 230px,transparent 231px),
  radial-gradient(circle at 8% 92%,rgba(255,255,255,.08) 0 300px,transparent 301px),
  linear-gradient(160deg,var(--deep),#000 140%)}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.35) 0%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 45%,rgba(0,0,0,.78) 100%)}
.nophoto .shade{display:none}
.top{position:absolute;top:56px;left:60px;right:60px}
.brand{display:inline-block;font:800 34px D;letter-spacing:-.01em;background:rgba(255,255,255,.94);color:var(--deep);padding:12px 22px;border-radius:999px}
.bottom{position:absolute;left:60px;right:60px;bottom:72px}
.eyebrow{display:inline-block;font:700 30px B;letter-spacing:.08em;text-transform:uppercase;color:#fff;opacity:.92;margin-bottom:18px}
.cr h1{font:800 104px/0.98 D;letter-spacing:-.025em;text-wrap:balance;text-shadow:0 2px 24px rgba(0,0,0,.25)}
.offer{display:inline-block;margin-top:30px;font:700 40px/1.15 B;background:var(--acc);color:#fff;padding:18px 28px;border-radius:18px;max-width:100%}
.story .s-mid{position:absolute;left:70px;right:70px;bottom:430px}
.story h1{font-size:132px}
.offer.tilt{transform:rotate(-3deg);font-size:46px;margin-top:40px;box-shadow:0 12px 30px rgba(0,0,0,.25)}
.nophoto h1{font-size:120px}
.nophoto .bottom{bottom:110px}
"""


def mock_feed(spec, c, photo):
    a = spec["ad1"]
    lang = spec.get("lang", "es")
    cta = a.get("cta") or t(spec, CTA[spec["action"]]["es"], CTA[spec["action"]]["en"])
    return f"""<div class=mf>
  <div class=mh><span class=av>{e(spec.get('initial') or spec['business'][:1])}</span>
    <div><b>{e(spec.get('handle') or spec['business'])}</b><small>{SPONSORED.get(lang,'Sponsored')}</small></div><span class=dots>•••</span></div>
  <div class=scale>{creative_feed(spec, c, photo)}</div>
  <div class=ctabar><div><small>{e(a.get('below') or spec.get('handle') or spec['business'])}</small></div><span class=ctab>{e(cta)}</span></div>
  <div class=icons><span>♡</span><span>💬</span><span>➤</span></div>
  <p class=cap><b>{e(spec.get('handle') or spec['business'])}</b> {e(a.get('primaryText'))}</p>
</div>"""


MF_CSS = """
body{width:1080px}
.mf{width:1080px;background:#fff;color:#111;font-family:B;padding-bottom:40px}
.mh{display:flex;align-items:center;gap:22px;padding:26px 30px}
.av{width:78px;height:78px;border-radius:50%;background:var(--acc);color:#fff;display:grid;place-items:center;font:800 38px D;box-shadow:0 0 0 4px #fff,0 0 0 7px var(--acc)}
.mh b{display:block;font:700 32px B}.mh small{font:400 26px B;color:#666}
.dots{margin-left:auto;font-size:30px;color:#333;letter-spacing:2px}
.ctabar{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:24px 30px;background:var(--light);border-bottom:1px solid #eee}
.ctabar small{font:600 28px B;color:#222}
.ctab{background:var(--acc);color:#fff;font:700 30px B;padding:16px 30px;border-radius:12px;white-space:nowrap}
.icons{display:flex;gap:34px;padding:22px 30px 8px;font-size:44px;color:#111}
.cap{padding:8px 30px 0;font:400 30px/1.4 B;color:#111}
.cap b{font-weight:700}
"""


def mock_story(spec, c, photo):
    a = spec["ad2"]
    lang = spec.get("lang", "es")
    cta = a.get("cta") or t(spec, CTA[spec["action"]]["es"], CTA[spec["action"]]["en"])
    return f"""<div class=ms>
  {creative_story(spec, c, photo)}
  <div class=sui>
    <div class=prog><i></i></div>
    <div class=sh><span class=av>{e(spec.get('initial') or spec['business'][:1])}</span><b>{e(spec.get('handle') or spec['business'])}</b><small>{SPONSORED.get(lang,'Sponsored')}</small></div>
    <div class=sbtn><span class=chev>︿</span><span class=pill>{e(cta)}</span></div>
  </div>
</div>"""


MS_CSS = """
.ms{position:relative;width:1080px;height:1920px;overflow:hidden;border-radius:0}
.sui{position:absolute;inset:0;pointer-events:none}
.prog{position:absolute;top:34px;left:30px;right:30px;height:7px;border-radius:4px;background:rgba(255,255,255,.4);overflow:hidden}
.prog i{display:block;width:38%;height:100%;background:#fff}
.sh{position:absolute;top:66px;left:30px;right:30px;display:flex;align-items:center;gap:18px;color:#fff;text-shadow:0 1px 8px rgba(0,0,0,.4)}
.sh .av{width:74px;height:74px;border-radius:50%;background:var(--acc);display:grid;place-items:center;font:800 36px D;border:3px solid #fff}
.sh b{font:700 32px B}.sh small{font:400 28px B;opacity:.85}
.sbtn{position:absolute;left:0;right:0;bottom:120px;display:flex;flex-direction:column;align-items:center;gap:10px}
.chev{color:#fff;font-size:44px;line-height:1}
.pill{background:#fff;color:#111;font:700 38px B;padding:22px 52px;border-radius:999px;box-shadow:0 8px 30px rgba(0,0,0,.25)}
"""


def page_html(spec, c, body, w, h):
    return f"""<!doctype html><html><head><meta charset=utf-8><style>{base_css(c)}{CR_CSS}{MF_CSS}{MS_CSS}
body{{width:{w}px;{('height:%dpx;' % h) if h else ''}}}
.scale{{width:1080px;height:1350px}}
</style></head><body>{body}</body></html>"""


# ---------- outputs ----------
def sample_page(spec, c, base):
    p = spec["plan"]
    lang = spec.get("lang", "es")
    L = lambda es, en: t(spec, es, en)
    title = L(f"2 anuncios de muestra para {spec['business']}", f"2 sample ads for {spec['business']}")
    return f"""<!doctype html><html lang="{ 'en' if lang=='en' else 'es'}"><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><meta name=robots content="noindex,nofollow">
<title>{e(title)} · Vexora</title><link rel=icon href="../../site-assets/icon.png">
<style>
:root{{--teal:#0D7C80;--ink:#14252A;--muted:#4D6267;--bg:#F4F7F7;--line:#D5E0E0;--acc:{c['accent']};color-scheme:light}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}
.w{{max-width:980px;margin:0 auto;padding:36px 16px 64px}}
.k{{font:600 .8rem ui-monospace,Menlo,monospace;color:var(--teal);letter-spacing:.04em}}
h1{{font-size:clamp(1.8rem,5vw,2.6rem);line-height:1.08;margin:10px 0 6px;letter-spacing:-.02em}}
.sub{{color:var(--muted);margin:0}}
.ads{{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:18px;margin-top:26px;align-items:start}}
@media(max-width:700px){{.ads{{grid-template-columns:minmax(0,1fr)}}}}
figure{{margin:0;background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden}}
figure img{{width:100%;display:block}}
figcaption{{padding:12px 16px;font-size:.92rem;color:var(--muted)}}figcaption b{{color:var(--ink)}}
.card{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px;margin-top:18px}}
.card h2{{margin:0 0 8px;font-size:1.15rem}}
ul{{margin:0;padding-left:20px}}li{{margin-top:6px}}
.cta{{display:inline-block;margin-top:14px;background:var(--acc);color:#fff;text-decoration:none;font-weight:700;padding:14px 20px;border-radius:12px}}
.fine{{font-size:.85rem;color:var(--muted);margin-top:18px}}
</style></head><body><div class=w>
<div class=k>// Vexora · {e(L('muestra privada','private sample'))}</div>
<h1>{e(title)}</h1>
<p class=sub>{e(L('Hechos para tu negocio. Con tus fotos y tu oferta reales, así se verían en Instagram y Facebook.','Made for your business. With your real photos and offer, this is how they would look on Instagram and Facebook.'))}</p>
<div class=ads>
<figure><img src="feed.jpg" alt="{e(L('Anuncio 1 en el feed','Ad 1 in the feed'))}: {e(spec['ad1']['headline'])}"><figcaption><b>{e(L('Anuncio 1 · Feed','Ad 1 · Feed'))}</b> · {e(spec['email'].get('ad1',''))}</figcaption></figure>
<figure><img src="story.jpg" alt="{e(L('Anuncio 2 en Stories','Ad 2 in Stories'))}: {e(spec['ad2']['headline'])}"><figcaption><b>{e(L('Anuncio 2 · Stories','Ad 2 · Stories'))}</b> · {e(spec['email'].get('ad2',''))}</figcaption></figure>
</div>
<div class=card><h2>{e(L('Plan de lanzamiento','Launch plan'))}</h2><ul>
<li><b>{e(L('Quién los ve','Who sees them'))}:</b> {e(p['who'])}</li>
<li><b>{e(L('Cuándo','When'))}:</b> {e(p['when'])}</li>
<li><b>{e(L('El botón','The button'))}:</b> {e(p.get('button') or spec['ad1'].get('cta') or CTA[spec['action']]['es' if lang!='en' else 'en'])}</li>
<li><b>{e(L('Qué medimos','What we track'))}:</b> {e(p['track'])}</li>
</ul>
<a class=cta href="mailto:vexorascale@gmail.com?subject={e(('Sí, empecemos · ' if lang!='en' else 'Yes, let us start · ')+spec['business'])}">{e(L('Quiero verlos en vivo','I want them live'))}</a></div>
<p class=fine>{e(L('Ejemplo de muestra. Textos y oferta se ajustan contigo antes de lanzar.','Sample only. Copy and offer get finalized with you before launch.'))} · Vexora</p>
</div></body></html>"""


def email_bodies(spec, base):
    m = spec["email"]
    p = spec["plan"]
    lang = spec.get("lang", "es")
    name = m.get("name") or ""
    biz = spec["business"]
    btn = lambda key: (spec[key].get("cta") or CTA[spec["action"]]["en" if lang == "en" else "es"])
    es_txt = f"""Hola{(' ' + name) if name else ''},

Aquí están los 2 anuncios de muestra para {biz}:

[ANUNCIO 1 · Feed] {m.get('ad1','')} → botón {btn('ad1')}
[ANUNCIO 2 · Stories] {m.get('ad2','')} → botón {btn('ad2')}

Verlos en grande: {base}/

Plan de lanzamiento:
• Quién los ve: {p['who']}
• Cuándo: {p['when']}
• Qué medimos: {p['track']}
• Pauta sugerida: {p['spend']} al día, que pagas directo a Meta.

Piloto de 30 días: $300. Armamos, lanzamos y ajustamos tus anuncios, con un reporte simple cada semana. Tus anuncios en vivo en 7 días, o tus primeros 30 días son gratis. Después, $500 al mes solo si quieres seguir.

¿Empezamos? Responde "SÍ" y te mando los pasos (toman 5 minutos).
¿Prefieres hablar? Responde con un horario y agendamos 15 minutos.

Sara
Vexora"""
    en_txt = f"""Hi{(' ' + name) if name else ''},

Here are the 2 sample ads for {biz}:

[AD 1 · Feed] {m.get('ad1','')} → {btn('ad1')} button
[AD 2 · Stories] {m.get('ad2','')} → {btn('ad2')} button

See them full size: {base}/

Launch plan:
• Who sees them: {p['who']}
• When: {p['when']}
• What we track: {p['track']}
• Suggested ad spend: {p['spend']} a day, paid directly to Meta.

30-day pilot: $300. We build, launch and adjust your ads, with a simple report every week. Your ads go live within 7 days, or your first 30 days are free. After that, $500 a month only if you want to continue.

Shall we start? Reply "YES" and I'll send the steps (they take 5 minutes).
Rather talk? Reply with a time and we'll set up 15 minutes.

Sara
Vexora"""
    addr = (m.get("address") or "").strip()
    if addr:
        es_txt += "\n" + addr
        en_txt += "\n" + addr
    txt = {"es": es_txt, "en": en_txt}.get(lang, es_txt + "\n\n— English —\n\n" + en_txt)

    def para(s):
        return "".join(f"<p style='margin:0 0 14px'>{e(x).replace(chr(10), '<br>')}</p>" for x in s.split("\n\n"))

    def block(s):
        head, rest = s.split("\n\n", 2)[0:2], s.split("\n\n", 2)[2]
        # insert images after the intro line
        imgs = f"""<table role=presentation cellpadding=0 cellspacing=0 style="width:100%;max-width:560px;margin:4px 0 18px"><tr>
<td style="width:56%;padding-right:8px;vertical-align:top"><a href="{base}/"><img src="{base}/feed-email.jpg" width="300" alt="Ad 1" style="width:100%;height:auto;border-radius:12px;border:1px solid #e3e8e8;display:block"></a></td>
<td style="width:44%;vertical-align:top"><a href="{base}/"><img src="{base}/story-email.jpg" width="236" alt="Ad 2" style="width:100%;height:auto;border-radius:12px;border:1px solid #e3e8e8;display:block"></a></td></tr></table>"""
        return para(head[0]) + para(head[1]) + imgs + para(rest)

    if lang in ("es", "en"):
        inner = block(txt)
    else:
        inner = block(es_txt) + "<hr style='border:0;border-top:1px solid #ddd;margin:22px 0'>" + para(en_txt)
    htm = f"""<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;font-size:15px;line-height:1.55;color:#14252A;max-width:600px">{inner}</div>"""
    subject = m.get("subject") or t(spec, f"tus 2 anuncios para {biz}", f"your 2 ads for {biz}")
    return subject, txt, htm


def render(pw_page, html_str, path, w, h, jpg_q=88):
    tmp = path + ".html"
    open(tmp, "w").write(html_str)
    pw_page.set_viewport_size({"width": w, "height": h or 800})
    pw_page.goto("file://" + tmp)
    pw_page.evaluate("document.fonts.ready")
    pw_page.wait_for_timeout(250)
    png = path + ".png"
    pw_page.screenshot(path=png, full_page=not h)
    Image.open(png).convert("RGB").save(path, quality=jpg_q, optimize=True, progressive=True)
    os.remove(png)
    os.remove(tmp)


def main(spec_path, out):
    out = os.path.abspath(out)
    spec = json.load(open(spec_path))
    sdir = os.path.dirname(os.path.abspath(spec_path))
    os.makedirs(out, exist_ok=True)
    work = os.path.join(sdir, "_work")
    os.makedirs(work, exist_ok=True)
    photos = [os.path.join(sdir, p) for p in spec.get("photos", []) if os.path.exists(os.path.join(sdir, p))]
    c = palette(photos, spec.get("colors"))
    i1, i2 = spec["ad1"].get("photo"), spec["ad2"].get("photo")
    p1 = prep_photo(photos[i1], os.path.join(work, "p1.jpg"), (1080, 1350)) if i1 is not None and i1 < len(photos) else None
    p2 = prep_photo(photos[i2], os.path.join(work, "p2.jpg"), (1080, 1920)) if i2 is not None and i2 < len(photos) else None
    base = f"{SITE}/s/{spec['token']}"
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        render(pg, page_html(spec, c, creative_feed(spec, c, p1), 1080, 1350), os.path.join(out, "feed-ad.jpg"), 1080, 1350)
        render(pg, page_html(spec, c, creative_story(spec, c, p2), 1080, 1920), os.path.join(out, "story-ad.jpg"), 1080, 1920)
        render(pg, page_html(spec, c, mock_feed(spec, c, p1), 1080, None), os.path.join(out, "feed.jpg"), 1080, None, 84)
        render(pg, page_html(spec, c, mock_story(spec, c, p2), 1080, 1920), os.path.join(out, "story.jpg"), 1080, 1920, 84)
        b.close()
    # small copies for the email body
    for n, wdt in (("feed", 600), ("story", 472)):
        im = Image.open(os.path.join(out, n + ".jpg"))
        im.thumbnail((wdt, 4000), Image.LANCZOS)
        im.save(os.path.join(out, n + "-email.jpg"), quality=82, optimize=True, progressive=True)
    # preview for Sara
    f, s = Image.open(os.path.join(out, "feed.jpg")), Image.open(os.path.join(out, "story.jpg"))
    H = 1200
    f = f.resize((int(f.width * H / f.height), H)); s = s.resize((int(s.width * H / s.height), H))
    pv = Image.new("RGB", (f.width + s.width + 60, H + 40), "#F4F7F7")
    pv.paste(f, (20, 20)); pv.paste(s, (f.width + 40, 20))
    pv.save(os.path.join(out, "preview.jpg"), quality=80)
    open(os.path.join(out, "index.html"), "w").write(sample_page(spec, c, base))
    subject, txt, htm = email_bodies(spec, base)
    open(os.path.join(out, "email.txt"), "w").write(txt)
    open(os.path.join(out, "email.html"), "w").write(htm)
    json.dump({"subject": subject, "page": base + "/", "colors": c}, open(os.path.join(out, "meta.json"), "w"), ensure_ascii=False, indent=1)
    shutil.rmtree(work, ignore_errors=True)
    print(json.dumps({"subject": subject, "page": base + "/", "colors": c}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
