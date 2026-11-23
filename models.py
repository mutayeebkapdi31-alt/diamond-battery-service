import os, sqlite3, uuid
from PIL import Image, ImageOps

DATA = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
UPLOADS = os.path.join(DATA, "uploads")
DBPATH = os.path.join(DATA, "site.db")
os.makedirs(UPLOADS, exist_ok=True)
ICONS = ["bat","inv","scan","ecm","arm","start","alt","ac","gas","shield","doc","wrench","phone"]

def F(n, l, k="text", **kw): return dict(n=n, l=l, k=k, **kw)
SORT, ACT = F("sort","Display order (small number shows first)","number"), F("active","Show on website","check")

ENT = {
 "products": dict(title="Batteries (catalogue)", one="battery", cols=["photo","name","brand","type","price","active"], fields=[
    F("brand","Brand","select",req=1), F("name","Model name","text"), F("type","Battery type (e.g. Car & SUV, Home inverter: tubular)","text"),
    F("cats","Suitable for (tick all that apply)","multi"), F("capacity","Capacity (e.g. 65 Ah)"), F("warranty","Warranty (e.g. 48 months)"),
    F("price","Price (or write 'Call for price')"), F("photo","Photo","image"), F("description","Short description","area"), SORT, ACT]),
 "brands": dict(title="Brands", one="brand", cols=["logo","name","blurb","active"], fields=[
    F("name","Brand name","text",req=1), F("blurb","Short line about the brand","area"), F("logo","Logo","image"), SORT, ACT]),
 "categories": dict(title="Vehicle categories", one="category", cols=["label","descr","active"], fields=[
    F("label","Name (e.g. 6 Wheeler)","text",req=1), F("short","Big tile text (e.g. 6)"), F("sub","Small tile text (e.g. Wheeler)"),
    F("descr","Example vehicles / description","area"), F("sizes","Typical battery sizes","area"), SORT, ACT]),
 "types": dict(title="Battery types", one="battery type", cols=["title","descr","active"], fields=[
    F("title","Type name","text",req=1), F("icon","Icon","icon"), F("descr","Short description","area"),
    F("capacity","Capacity range"), F("suited","Suited for / vehicles"), F("features","Key features"), SORT, ACT]),
 "services": dict(title="Services", one="service", cols=["title","descr","active"], fields=[
    F("title","Service name","text",req=1), F("icon","Icon","icon"), F("descr","Short description","area"),
    F("items","What is included (one point per line)","area"), SORT, ACT]),
 "warranties": dict(title="Warranty & assurance", one="warranty card", cols=["title","descr","active"], fields=[
    F("title","Title","text",req=1), F("icon","Icon","icon"), F("descr","Text","area"), SORT, ACT]),
 "signs": dict(title="Car tips (warning signs)", one="tip", cols=["title","descr","service","active"], fields=[
    F("title","Sign (e.g. Dim headlights)","text",req=1), F("descr","Explanation","area"), F("icon","Icon","icon"),
    F("service","Links to service","select"), SORT, ACT]),
 "faqs": dict(title="FAQ", one="question", cols=["q","active"], fields=[
    F("q","Question","text",req=1), F("a","Answer","area"), SORT, ACT]),
 "reviews": dict(title="Customer reviews", one="review", cols=["text","author","active"], fields=[
    F("text","Review","area",req=1), F("author","Customer name"), SORT, ACT]),
 "stats": dict(title="Highlights (numbers)", one="highlight", cols=["number","label","active"], fields=[
    F("number","Number","number"), F("label","Label (e.g. car brands serviced)","text",req=1), SORT, ACT]),
 "gallery": dict(title="Photo gallery", one="photo", cols=["photo","caption","active"], fields=[
    F("photo","Photo","image",req=1), F("caption","Caption"), SORT, ACT]),
}
SETTINGS = [
 F("name","Shop name","text",req=1), F("owner","Owner name"), F("phone","Main phone (with 91, no spaces, e.g. 919422480596)"),
 F("phone_display","Main phone as shown (e.g. 94224 80596)"), F("phone2","Second phone (with 91)"), F("phone2_display","Second phone as shown"),
 F("address","Address","area"), F("hours","Opening hours (e.g. Mon-Sat 9 AM - 8 PM)"), F("maps_embed","Google Maps embed link"),
 F("hero_tag","Small tag above the headline"), F("hero_lead","Paragraph under the headline","area"),
 F("warranty_note","Warranty note","area"), F("meta_desc","Search engine description","area"),
 F("show_ph","Show dashed placeholder boxes where content is empty","check"),
]
SETTING_DEFAULTS = dict(name="Diamond Battery Service", owner="Imtiyaz M. Mangoli", phone="919422480596", phone_display="94224 80596",
 phone2="919673710500", phone2_display="96737 10500", address="Opp. Spectra Co., Kalyan-Murbad Road, Sonarpada, Murbad, Dist. Thane 421401",
 hours="Opening hours: please add in Admin > Settings", maps_embed="https://www.google.com/maps?q=Diamond+Battery+Service+Murbad&output=embed",
 hero_tag="Kalyan-Murbad Road, Murbad", hero_lead="One workshop for everything that powers and cools your car. Branded batteries, expert repairs and honest advice.",
 warranty_note="Warranty period depends on the battery brand and model. Please ask us for details before buying and keep your warranty card and bill.",
 meta_desc="Car, two wheeler, truck and home inverter batteries, car scanning, ECM, starter, alternator and car A/C service in Murbad.", show_ph="1")

def db():
    c = sqlite3.connect(DBPATH); c.row_factory = sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c

def _coltype(f): return "INTEGER DEFAULT 0" if f["k"] in ("number","check") else "TEXT DEFAULT ''"

def init():
    with db() as c:
        c.execute("CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS admin(id INTEGER PRIMARY KEY, username TEXT, hash TEXT)")
        c.execute("""CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, service TEXT,
            vehicle TEXT, message TEXT, status TEXT DEFAULT 'New', created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        for e, d in ENT.items():
            cols = ",".join(f"{f['n']} {_coltype(f)}" for f in d["fields"])
            c.execute(f"CREATE TABLE IF NOT EXISTS {e}(id INTEGER PRIMARY KEY AUTOINCREMENT,{cols})")
            have = {r[1] for r in c.execute(f"PRAGMA table_info({e})")}
            for f in d["fields"]:
                if f["n"] not in have: c.execute(f"ALTER TABLE {e} ADD COLUMN {f['n']} {_coltype(f)}")
        have = {r[1] for r in c.execute("PRAGMA table_info(bookings)")}
        if "status" not in have: c.execute("ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT 'New'")
        for k, v in SETTING_DEFAULTS.items(): c.execute("INSERT OR IGNORE INTO settings VALUES(?,?)", (k, v))

def settings():
    with db() as c: return {r["key"]: r["value"] for r in c.execute("SELECT * FROM settings")}

def rows(e, active_only=False):
    q = f"SELECT * FROM {e}" + (" WHERE active=1" if active_only else "") + " ORDER BY sort,id"
    with db() as c: return [dict(r) for r in c.execute(q)]

def row(e, i):
    with db() as c:
        r = c.execute(f"SELECT * FROM {e} WHERE id=?", (i,)).fetchone()
    return dict(r) if r else None

def save(e, i, data):
    names = [f["n"] for f in ENT[e]["fields"]]
    with db() as c:
        if i:
            c.execute(f"UPDATE {e} SET " + ",".join(f"{n}=?" for n in names) + " WHERE id=?", [data[n] for n in names] + [i])
            return i
        cur = c.execute(f"INSERT INTO {e}({','.join(names)}) VALUES({','.join('?'*len(names))})", [data[n] for n in names])
        return cur.lastrowid

def remove(e, i):
    r = row(e, i)
    if r:
        for f in ENT[e]["fields"]:
            if f["k"] == "image": drop_file(r.get(f["n"]))
        with db() as c: c.execute(f"DELETE FROM {e} WHERE id=?", (i,))

def move(e, i, d):
    ids = [r["id"] for r in rows(e)]
    if i not in ids: return
    p = ids.index(i); q = p + d
    if 0 <= q < len(ids):
        ids[p], ids[q] = ids[q], ids[p]
        with db() as c:
            for n, x in enumerate(ids): c.execute(f"UPDATE {e} SET sort=? WHERE id=?", (n + 1, x))

def options(f):
    n = f["n"]
    if n == "brand": return [(str(r["id"]), r["name"]) for r in rows("brands")]
    if n == "cats": return [(str(r["id"]), r["label"]) for r in rows("categories")]
    if n == "service": return [("", "(none)")] + [(r["title"], r["title"]) for r in rows("services")]
    if n == "icon": return [(x, x) for x in ICONS]
    return []

def drop_file(name):
    if name:
        p = os.path.join(UPLOADS, os.path.basename(name))
        if os.path.isfile(p): os.remove(p)

def save_image(fs):
    """Validate, orient, shrink and store an uploaded image. Returns filename or None."""
    try:
        im = Image.open(fs.stream); im.load()
    except Exception:
        return None
    im = ImageOps.exif_transpose(im); im.thumbnail((1200, 1200))
    alpha = im.mode in ("RGBA", "LA", "P")
    name = uuid.uuid4().hex + (".png" if alpha else ".jpg")
    if alpha: im.convert("RGBA").save(os.path.join(UPLOADS, name), "PNG", optimize=True)
    else: im.convert("RGB").save(os.path.join(UPLOADS, name), "JPEG", quality=82, optimize=True)
    return name
