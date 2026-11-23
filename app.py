import os, re, io, csv, time, secrets
from collections import defaultdict
from flask import (Flask, render_template, request, jsonify, session, redirect, url_for,
                   abort, flash, send_from_directory, Response)
from werkzeug.security import generate_password_hash, check_password_hash
import models as M, seed
from config import ADMIN_USERNAME, ADMIN_PASSWORD

app = Flask(__name__)
app.config.update(MAX_CONTENT_LENGTH=25 * 1024 * 1024, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  PERMANENT_SESSION_LIFETIME=60 * 60 * 12)
_kf = os.path.join(M.DATA, "secret.key")
if os.environ.get("SECRET_KEY"): app.secret_key = os.environ["SECRET_KEY"]
else:
    if not os.path.exists(_kf): open(_kf, "w").write(secrets.token_hex(32))
    app.secret_key = open(_kf).read().strip()

def boot():
    M.init(); seed.run()
    with M.db() as c:
        if not c.execute("SELECT 1 FROM admin").fetchone():
            c.execute("INSERT INTO admin VALUES(1,?,?)", (ADMIN_USERNAME, generate_password_hash(os.environ.get("ADMIN_PASSWORD", ADMIN_PASSWORD))))
boot()

# ---------------- public site ----------------
def ctx():
    return dict(shop=M.settings(), r="", brands=M.rows("brands", 1), cats=M.rows("categories", 1), services=M.rows("services", 1))

@app.route("/")
def home():
    return render_template("index.html", warranties=M.rows("warranties", 1), signs=M.rows("signs", 1), faqs=M.rows("faqs", 1),
                           reviews=M.rows("reviews", 1), stats=M.rows("stats", 1), gallery=M.rows("gallery", 1), **ctx())

@app.route("/batteries")
def batteries():
    c = ctx(); c["r"] = "/"
    names = {str(b["id"]): b["name"] for b in c["brands"]}
    prods = [p for p in M.rows("products", 1) if p["brand"] in names]
    return render_template("batteries.html", types=M.rows("types", 1), products=prods, names=names, **c)

@app.route("/uploads/<path:name>")
def uploads(name):
    return send_from_directory(M.UPLOADS, name, max_age=86400)

_hits = defaultdict(list)
def limited(key, n, secs):
    now = time.time(); _hits[key] = [t for t in _hits[key] if now - t < secs]
    if len(_hits[key]) >= n: return True
    _hits[key].append(now); return False

@app.post("/api/book")
def book():
    d = request.get_json(silent=True) or {}
    if d.get("website"): return jsonify(ok=True)           # honeypot
    if limited("book" + (request.remote_addr or ""), 8, 3600): return jsonify(ok=False, error="Too many requests. Please call us."), 429
    name, phone = (d.get("name") or "").strip(), re.sub(r"\D", "", d.get("phone") or "")
    if len(name) < 2 or len(phone) < 10:
        return jsonify(ok=False, error="Enter your name and a valid 10-digit phone number."), 400
    with M.db() as c:
        c.execute("INSERT INTO bookings(name,phone,service,vehicle,message) VALUES(?,?,?,?,?)",
                  (name[:80], phone[-12:], (d.get("service") or "")[:80], (d.get("vehicle") or "")[:80], (d.get("message") or "")[:500]))
    return jsonify(ok=True)

# ---------------- admin: auth + csrf ----------------
def token():
    if "csrf" not in session: session["csrf"] = secrets.token_hex(16)
    return session["csrf"]
app.jinja_env.globals["csrf"] = token

@app.before_request
def guard():
    p = request.path
    if not p.startswith("/admin"): return
    if request.method == "POST" and not secrets.compare_digest(request.form.get("_csrf", ""), session.get("csrf", "x")):
        abort(400)
    if p != "/admin/login" and not session.get("admin"): return redirect(url_for("login"))

@app.after_request
def headers(r):
    r.headers.setdefault("X-Content-Type-Options", "nosniff"); r.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    if request.path.startswith("/admin"): r.headers["Cache-Control"] = "no-store"
    return r

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    err = ""
    if request.method == "POST":
        ip = request.remote_addr or ""
        if limited("login" + ip, 8, 600): err = "Too many attempts. Wait 10 minutes."
        else:
            with M.db() as c: a = c.execute("SELECT * FROM admin WHERE id=1").fetchone()
            if request.form.get("u", "").strip() == a["username"] and check_password_hash(a["hash"], request.form.get("p", "")):
                session.clear(); session["admin"] = 1; session.permanent = True
                return redirect(url_for("dash"))
            err = "Wrong username or password."
    return render_template("admin/login.html", err=err, shop=M.settings())

@app.route("/admin/logout", methods=["POST"])
def logout():
    session.clear(); return redirect(url_for("login"))

def page(tpl, **kw):
    return render_template("admin/" + tpl, shop=M.settings(), ent=M.ENT, **kw)

@app.route("/admin/")
@app.route("/admin")
def dash():
    with M.db() as c:
        n = lambda q: c.execute(q).fetchone()[0]
        stats = dict(new=n("SELECT COUNT(*) FROM bookings WHERE status='New'"), total=n("SELECT COUNT(*) FROM bookings"),
                     products=n("SELECT COUNT(*) FROM products WHERE active=1"), nophoto=n("SELECT COUNT(*) FROM products WHERE photo='' OR photo IS NULL"),
                     noname=n("SELECT COUNT(*) FROM products WHERE name='' OR name IS NULL"), gallery=n("SELECT COUNT(*) FROM gallery"),
                     a=c.execute("SELECT hash FROM admin WHERE id=1").fetchone()[0])
    stats["defpw"] = check_password_hash(stats.pop("a"), ADMIN_PASSWORD)
    recent = [dict(r) for r in M.db().execute("SELECT * FROM bookings ORDER BY id DESC LIMIT 5")]
    return page("dash.html", s=stats, recent=recent)

# ---------------- admin: bookings ----------------
STATUSES = ["New", "Called", "Completed", "Cancelled"]
@app.route("/admin/bookings")
def bookings():
    st, q = request.args.get("status", ""), request.args.get("q", "").strip()
    sql, args = "SELECT * FROM bookings WHERE 1=1", []
    if st in STATUSES: sql += " AND status=?"; args.append(st)
    if q: sql += " AND (name LIKE ? OR phone LIKE ? OR service LIKE ? OR vehicle LIKE ?)"; args += [f"%{q}%"] * 4
    with M.db() as c: rows = [dict(r) for r in c.execute(sql + " ORDER BY id DESC", args)]
    return page("bookings.html", rows=rows, statuses=STATUSES, st=st, q=q)

@app.post("/admin/bookings/<int:i>/status")
def booking_status(i):
    s = request.form.get("status")
    if s in STATUSES:
        with M.db() as c: c.execute("UPDATE bookings SET status=? WHERE id=?", (s, i))
    return redirect(request.referrer or url_for("bookings"))

@app.post("/admin/bookings/<int:i>/delete")
def booking_delete(i):
    with M.db() as c: c.execute("DELETE FROM bookings WHERE id=?", (i,))
    flash("Booking deleted."); return redirect(url_for("bookings"))

@app.route("/admin/bookings.csv")
def bookings_csv():
    out = io.StringIO(); w = csv.writer(out); w.writerow(["id", "date", "name", "phone", "service", "vehicle", "message", "status"])
    with M.db() as c:
        for r in c.execute("SELECT * FROM bookings ORDER BY id DESC"):
            w.writerow([r["id"], r["created"], r["name"], r["phone"], r["service"], r["vehicle"], r["message"], r["status"]])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=bookings.csv"})

# ---------------- admin: settings + password ----------------
@app.route("/admin/settings", methods=["GET", "POST"])
def settings_page():
    if request.method == "POST":
        with M.db() as c:
            for f in M.SETTINGS:
                v = ("1" if request.form.get(f["n"]) else "0") if f["k"] == "check" else request.form.get(f["n"], "").strip()
                c.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (f["n"], v))
        flash("Settings saved."); return redirect(url_for("settings_page"))
    return page("form.html", title="Shop settings", fields=M.SETTINGS, vals=M.settings(), opts=M.options, action=url_for("settings_page"), back=None, e=None, i=None)

@app.route("/admin/password", methods=["GET", "POST"])
def password():
    err = ""
    if request.method == "POST":
        with M.db() as c: a = c.execute("SELECT * FROM admin WHERE id=1").fetchone()
        u, n, n2 = request.form.get("u", "").strip(), request.form.get("n", ""), request.form.get("n2", "")
        if not check_password_hash(a["hash"], request.form.get("old", "")): err = "Current password is wrong."
        elif len(n) < 8: err = "New password must be at least 8 characters."
        elif n != n2: err = "New passwords do not match."
        else:
            with M.db() as c: c.execute("UPDATE admin SET username=?, hash=? WHERE id=1", (u or a["username"], generate_password_hash(n)))
            flash("Login details updated."); return redirect(url_for("dash"))
    with M.db() as c: cur = c.execute("SELECT username FROM admin").fetchone()[0]
    return page("password.html", err=err, cur=cur)

# ---------------- admin: generic content editor ----------------
def parse(e, old=None):
    data, newfiles = {}, []
    for f in M.ENT[e]["fields"]:
        n, k = f["n"], f["k"]
        if k == "check": data[n] = 1 if request.form.get(n) else 0
        elif k == "number":
            try: data[n] = int(request.form.get(n) or 0)
            except ValueError: data[n] = 0
        elif k == "multi": data[n] = ",".join(request.form.getlist(n))
        elif k == "image":
            data[n] = (old or {}).get(n, "") or ""
            up = request.files.get(n)
            if request.form.get("rm_" + n): M.drop_file(data[n]); data[n] = ""
            if up and up.filename:
                nm = M.save_image(up)
                if nm: M.drop_file(data[n]); data[n] = nm
                else: flash("That file is not a valid image (use JPG or PNG).")
        else: data[n] = request.form.get(n, "").strip()
    return data

def label(e, f, r):
    v = r.get(f["n"], "")
    if f["k"] == "image": return ("img", v)
    if f["k"] == "check": return ("txt", "Visible" if v else "Hidden")
    if f["k"] in ("select", "multi") and f["n"] in ("brand", "cats"):
        m = dict(M.options(f)); return ("txt", ", ".join(m.get(x, "") for x in str(v).split(",") if x))
    return ("txt", (str(v)[:90] + ("..." if len(str(v)) > 90 else "")) if v not in ("", None) else "")

@app.route("/admin/c/<e>")
def clist(e):
    if e not in M.ENT: abort(404)
    d = M.ENT[e]; fm = {f["n"]: f for f in d["fields"]}
    rws = [dict(id=r["id"], cells=[label(e, fm[c], r) for c in d["cols"]], on=r.get("active", 1)) for r in M.rows(e)]
    return page("list.html", e=e, d=d, heads=[fm[c]["l"].split(" (")[0] for c in d["cols"]], rows=rws)

@app.route("/admin/c/<e>/new", methods=["GET", "POST"])
@app.route("/admin/c/<e>/<int:i>", methods=["GET", "POST"])
def cedit(e, i=None):
    if e not in M.ENT: abort(404)
    d = M.ENT[e]; old = M.row(e, i) if i else None
    if i and not old: abort(404)
    if request.method == "POST":
        data = parse(e, old)
        miss = [f["l"] for f in d["fields"] if f.get("req") and not data[f["n"]]]
        if miss: flash("Please fill: " + ", ".join(miss))
        else:
            M.save(e, i, data); flash("Saved."); return redirect(url_for("clist", e=e))
        vals = {**(old or {}), **data}
    else:
        vals = old or {f["n"]: (1 if f["k"] == "check" else 0 if f["k"] == "number" else "") for f in d["fields"]}
        if not old and "sort" in vals: vals["sort"] = len(M.rows(e)) + 1
    return page("form.html", title=("Edit " if i else "Add ") + d["one"], fields=d["fields"], vals=vals, opts=M.options,
                action=request.path, back=url_for("clist", e=e), e=e, i=i)

@app.post("/admin/c/<e>/<int:i>/delete")
def cdelete(e, i):
    if e not in M.ENT: abort(404)
    M.remove(e, i); flash("Deleted."); return redirect(url_for("clist", e=e))

@app.post("/admin/c/<e>/<int:i>/move/<int:d>")
def cmove(e, i, d):
    if e not in M.ENT: abort(404)
    M.move(e, i, -1 if d == 0 else 1); return redirect(url_for("clist", e=e))

@app.errorhandler(413)
def toobig(_): return "File too large (max 25 MB).", 413

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
