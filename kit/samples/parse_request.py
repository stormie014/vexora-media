#!/usr/bin/env python3
"""Parse one FormSubmit request email into request.json + photos.

Usage: python3 parse_request.py RAW_SOURCE OUT_DIR
  RAW_SOURCE: either the JSON saved from Gmail get_message (messageFormat RAW) — inline result
              pasted to a file or the tool-results file Claude Code saved — or a plain .eml file.
Writes OUT_DIR/request.json {business, link, email, action, actionKey, when, whenKey, whatsapp, date, photos:[...]}
and OUT_DIR/photos/1.jpg ... (normalized to JPEG, max 2000px).
"""
import base64, email, email.policy, html, io, json, os, re, sys
from email.utils import parsedate_to_datetime
from PIL import Image, ImageOps

ACTION = {"pedir": "order", "order": "order", "reservar": "book", "book": "book",
          "llamar": "call", "call": "call", "cotizar": "quote", "quote": "quote",
          "pedidos de fiestas": "order", "holiday": "order"}
WHEN = {"este mes": "now", "this month": "now", "más adelante": "later", "mas adelante": "later",
        "later": "later", "solo mirando": "looking", "just looking": "looking"}


def load_raw(src):
    data = open(src, "rb").read()
    try:
        j = json.loads(data)
        if isinstance(j, list):  # some tool-result files wrap content blocks
            j = next((json.loads(x["text"]) for x in j if isinstance(x, dict) and x.get("type") == "text"), {})
        raw = j["raw"]
        raw += "=" * (-len(raw) % 4)
        return base64.urlsafe_b64decode(raw)
    except (ValueError, KeyError, TypeError):
        return data


def fields_from(msg):
    body_html = body_txt = ""
    for part in msg.walk():
        ct = part.get_content_type()
        if part.get_content_maintype() == "multipart" or part.get_filename():
            continue
        if ct == "text/html" and not body_html:
            body_html = part.get_content()
        elif ct == "text/plain" and not body_txt:
            body_txt = part.get_content()
    f = {}
    if body_html:
        for k, v in re.findall(r"<tr[^>]*>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>", body_html, re.S | re.I):
            k = html.unescape(re.sub(r"<[^>]+>", "", k)).strip()
            v = html.unescape(re.sub(r"<[^>]+>", " ", v)).strip()
            if k and k.lower() not in ("name", "nombre"):
                f[k] = re.sub(r"\s+", " ", v)
    if not f and body_txt:
        for line in body_txt.splitlines():
            m = re.match(r"\s*([A-Za-zÁÉÍÓÚáéíóúñ_ ]{3,30})\s*[:|]\s*(.+)", line)
            if m:
                f[m.group(1).strip()] = m.group(2).strip()
    return f


def pick(f, *keys):
    for k in f:
        kk = k.lower().replace("_", " ")
        if any(x in kk for x in keys):
            return f[k]
    return ""


def keymap(val, table):
    v = (val or "").lower()
    for k, out in table.items():
        if k in v:
            return out
    return ""


def main(src, out):
    os.makedirs(os.path.join(out, "photos"), exist_ok=True)
    msg = email.message_from_bytes(load_raw(src), policy=email.policy.default)
    f = fields_from(msg)
    photos = []
    for part in msg.walk():
        fn = part.get_filename()
        if not fn or part.get_content_maintype() != "image":
            continue
        try:
            im = ImageOps.exif_transpose(Image.open(io.BytesIO(part.get_payload(decode=True)))).convert("RGB")
            im.thumbnail((2000, 2000))
            p = os.path.join(out, "photos", f"{len(photos) + 1}.jpg")
            im.save(p, quality=90)
            photos.append(f"photos/{len(photos) + 1}.jpg")
        except Exception as ex:
            print("skip attachment", fn, ex, file=sys.stderr)
    action = pick(f, "acci", "action")
    when = pick(f, "cuándo", "cuando", "when")
    try:
        date = parsedate_to_datetime(msg["Date"]).isoformat()
    except Exception:
        date = ""
    req = {
        "business": pick(f, "negocio", "business"),
        "link": pick(f, "instagram", "web"),
        "email": pick(f, "email", "correo"),
        "action": action, "actionKey": keymap(action, ACTION) or "order",
        "when": when, "whenKey": keymap(when, WHEN) or "later",
        "whatsapp": pick(f, "whatsapp"),
        "about": pick(f, "sobre", "about"),
        "date": date, "messageId": msg["Message-ID"] or "",
        "photos": photos, "allFields": f,
    }
    json.dump(req, open(os.path.join(out, "request.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in req.items() if k != "allFields"}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
