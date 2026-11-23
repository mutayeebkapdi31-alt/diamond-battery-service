import os
import io
import uuid

from PIL import Image, ImageOps
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


# ---------------- BASIC CONFIGURATION ----------------

DATA = os.environ.get(
    "DATA_DIR",
    os.path.dirname(os.path.abspath(__file__))
)

UPLOADS = os.path.join(DATA, "uploads")


# ---------------- DATABASE CONFIGURATION ----------------

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = int(os.environ.get("DB_PORT", "6543"))
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


# ---------------- SUPABASE STORAGE CONFIGURATION ----------------

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY"
)

STORAGE_BUCKET = "diamond-uploads"

_supabase_client = None


def storage_client():
    """Create and reuse the Supabase client."""

    global _supabase_client

    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "Supabase Storage credentials are missing. "
            "Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
        )

    if _supabase_client is None:
        _supabase_client = create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_ROLE_KEY
        )

    return _supabase_client


def image_url(name):
    """Return the public URL of an uploaded image."""

    if not name:
        return ""

    safe_name = os.path.basename(name)

    return (
        storage_client()
        .storage
        .from_(STORAGE_BUCKET)
        .get_public_url(safe_name)
    )


# ---------------- ICONS ----------------

ICONS = [
    "bat", "inv", "scan", "ecm", "arm", "start", "alt",
    "ac", "gas", "shield", "doc", "wrench", "phone"
]


# ---------------- FIELD HELPER ----------------

def F(n, l, k="text", **kw):
    return dict(n=n, l=l, k=k, **kw)


SORT = F(
    "sort",
    "Display order (small number shows first)",
    "number"
)

ACT = F(
    "active",
    "Show on website",
    "check"
)


# ---------------- CONTENT MANAGEMENT ----------------

ENT = {

    "products": dict(
        title="Batteries (catalogue)",
        one="battery",
        cols=["photo", "name", "brand", "type", "price", "active"],
        fields=[
            F("brand", "Brand name", "select", req=1),
            F("name", "Model name", "text"),
            F("type", "Battery type", "text"),
            F("cats", "Suitable for (tick all that apply)", "multi"),
            F("capacity", "Capacity"),
            F("warranty", "Warranty"),
            F("price", "Price"),
            F("photo", "Photo", "image"),
            F("description", "Short description", "area"),
            SORT,
            ACT
        ]
    ),

    "brands": dict(
        title="Brands",
        one="brand",
        cols=["logo", "name", "blurb", "active"],
        fields=[
            F("name", "Brand name", "text", req=1),
            F("blurb", "Short line about the brand", "area"),
            F("logo", "Logo", "image"),
            SORT,
            ACT
        ]
    ),

    "categories": dict(
        title="Vehicle categories",
        one="category",
        cols=["label", "descr", "active"],
        fields=[
            F("label", "Name", "text", req=1),
            F("short", "Big tile text"),
            F("sub", "Small tile text"),
            F("descr", "Example vehicles / description", "area"),
            F("sizes", "Typical battery sizes", "area"),
            SORT,
            ACT
        ]
    ),

    "types": dict(
        title="Battery types",
        one="battery type",
        cols=["title", "descr", "active"],
        fields=[
            F("title", "Type name", "text", req=1),
            F("icon", "Icon", "icon"),
            F("descr", "Short description", "area"),
            F("capacity", "Capacity range"),
            F("suited", "Suited for / vehicles"),
            F("features", "Key features"),
            SORT,
            ACT
        ]
    ),

    "services": dict(
        title="Services",
        one="service",
        cols=["title", "descr", "active"],
        fields=[
            F("title", "Service name", "text", req=1),
            F("icon", "Icon", "icon"),
            F("descr", "Short description", "area"),
            F("items", "What is included (one point per line)", "area"),
            SORT,
            ACT
        ]
    ),

    "warranties": dict(
        title="Warranty & assurance",
        one="warranty card",
        cols=["title", "descr", "active"],
        fields=[
            F("title", "Title", "text", req=1),
            F("icon", "Icon", "icon"),
            F("descr", "Text", "area"),
            SORT,
            ACT
        ]
    ),

    "signs": dict(
        title="Car tips (warning signs)",
        one="tip",
        cols=["title", "descr", "service", "active"],
        fields=[
            F("title", "Sign", "text", req=1),
            F("descr", "Explanation", "area"),
            F("icon", "Icon", "icon"),
            F("service", "Links to service", "select"),
            SORT,
            ACT
        ]
    ),

    "faqs": dict(
        title="FAQ",
        one="question",
        cols=["q", "active"],
        fields=[
            F("q", "Question", "text", req=1),
            F("a", "Answer", "area"),
            SORT,
            ACT
        ]
    ),

    "reviews": dict(
        title="Customer reviews",
        one="review",
        cols=["text", "author", "active"],
        fields=[
            F("text", "Review", "area", req=1),
            F("author", "Customer name"),
            SORT,
            ACT
        ]
    ),

    "stats": dict(
        title="Highlights (numbers)",
        one="highlight",
        cols=["number", "label", "active"],
        fields=[
            F("number", "Number", "number"),
            F("label", "Label", "text", req=1),
            SORT,
            ACT
        ]
    ),

    "gallery": dict(
        title="Photo gallery",
        one="photo",
        cols=["photo", "caption", "active"],
        fields=[
            F("photo", "Photo", "image", req=1),
            F("caption", "Caption"),
            SORT,
            ACT
        ]
    )
}


# ---------------- SHOP SETTINGS ----------------

SETTINGS = [
    F("name", "Shop name", "text", req=1),
    F("owner", "Owner name"),
    F("phone", "Main phone"),
    F("phone_display", "Main phone as shown"),
    F("phone2", "Second phone"),
    F("phone2_display", "Second phone as shown"),
    F("address", "Address", "area"),
    F("hours", "Opening hours"),
    F("maps_embed", "Google Maps embed link"),
    F("hero_tag", "Small tag above the headline"),
    F("hero_lead", "Paragraph under the headline", "area"),
    F("warranty_note", "Warranty note", "area"),
    F("meta_desc", "Search engine description", "area"),
    F("show_ph", "Show placeholder boxes", "check")
]


SETTING_DEFAULTS = dict(
    name="Diamond Battery Service",
    owner="Imtiyaz M. Mangoli",
    phone="919422480596",
    phone_display="94224 80596",
    phone2="919673710500",
    phone2_display="96737 10500",
    address="Opp. Spectra Co., Kalyan-Murbad Road, Sonarpada, Murbad, Dist. Thane 421401",
    hours="Opening hours: please add in Admin > Settings",
    maps_embed="https://www.google.com/maps?q=Diamond+Battery+Service+Murbad&output=embed",
    hero_tag="Kalyan-Murbad Road, Murbad",
    hero_lead="One workshop for everything that powers and cools your car. Branded batteries, expert repairs and honest advice.",
    warranty_note="Warranty period depends on the battery brand and model. Please ask us for details before buying and keep your warranty card and bill.",
    meta_desc="Car, two wheeler, truck and home inverter batteries, car scanning, ECM, starter, alternator and car A/C service in Murbad.",
    show_ph="1"
)


# ---------------- POSTGRESQL DATABASE ----------------

def db():
    """Connect to the Supabase PostgreSQL database."""

    if not all([DB_HOST, DB_USER, DB_PASSWORD]):
        raise RuntimeError(
            "Supabase database credentials are missing."
        )

    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require",
        row_factory=dict_row
    )


# ---------------- DATABASE INITIALIZATION ----------------

def init():
    """Insert default settings if they do not already exist."""

    with db() as c:

        for key, value in SETTING_DEFAULTS.items():

            c.execute(
                """
                INSERT INTO settings (key, value)
                VALUES (%s, %s)
                ON CONFLICT (key) DO NOTHING
                """,
                (key, str(value))
            )


# ---------------- SETTINGS ----------------

def settings():

    with db() as c:

        result = c.execute(
            "SELECT key, value FROM settings"
        ).fetchall()

    return {
        r["key"]: r["value"]
        for r in result
    }


# ---------------- CONTENT ROWS ----------------

def rows(e, active_only=False):

    if e not in ENT:
        raise ValueError("Invalid content table")

    query = f'SELECT * FROM "{e}"'

    if active_only:
        query += " WHERE active = 1"

    query += " ORDER BY sort, id"

    with db() as c:
        return c.execute(query).fetchall()


def row(e, i):

    if e not in ENT:
        raise ValueError("Invalid content table")

    with db() as c:

        result = c.execute(
            f'SELECT * FROM "{e}" WHERE id = %s',
            (i,)
        ).fetchone()

    return result


# ---------------- SAVE CONTENT ----------------

def save(e, i, data):

    if e not in ENT:
        raise ValueError("Invalid content table")

    names = [
        f["n"]
        for f in ENT[e]["fields"]
    ]

    values = [
        data.get(n, "")
        for n in names
    ]

    with db() as c:

        if i:

            assignments = ", ".join(
                f'"{n}" = %s'
                for n in names
            )

            result = c.execute(
                f"""
                UPDATE "{e}"
                SET {assignments}
                WHERE id = %s
                RETURNING id
                """,
                values + [i]
            ).fetchone()

            return result["id"] if result else None

        columns = ", ".join(
            f'"{n}"'
            for n in names
        )

        placeholders = ", ".join(
            ["%s"] * len(names)
        )

        result = c.execute(
            f"""
            INSERT INTO "{e}" ({columns})
            VALUES ({placeholders})
            RETURNING id
            """,
            values
        ).fetchone()

        return result["id"]


# ---------------- DELETE CONTENT ----------------

def remove(e, i):

    if e not in ENT:
        raise ValueError("Invalid content table")

    existing = row(e, i)

    if existing:

        for field in ENT[e]["fields"]:

            if field["k"] == "image":
                drop_file(existing.get(field["n"]))

        with db() as c:

            c.execute(
                f'DELETE FROM "{e}" WHERE id = %s',
                (i,)
            )


# ---------------- CHANGE DISPLAY ORDER ----------------

def move(e, i, direction):

    if e not in ENT:
        raise ValueError("Invalid content table")

    current_rows = rows(e)

    ids = [
        r["id"]
        for r in current_rows
    ]

    if i not in ids:
        return

    position = ids.index(i)
    new_position = position + direction

    if 0 <= new_position < len(ids):

        ids[position], ids[new_position] = (
            ids[new_position],
            ids[position]
        )

        with db() as c:

            for number, item_id in enumerate(ids, start=1):

                c.execute(
                    f'UPDATE "{e}" SET sort = %s WHERE id = %s',
                    (number, item_id)
                )


# ---------------- DROPDOWN OPTIONS ----------------

def options(f):

    n = f["n"]

    if n == "brand":

        return [
            (str(r["id"]), r["name"])
            for r in rows("brands")
        ]

    if n == "cats":

        return [
            (str(r["id"]), r["label"])
            for r in rows("categories")
        ]

    if n == "service":

        return [("", "(none)")] + [
            (r["title"], r["title"])
            for r in rows("services")
        ]

    if n == "icon":

        return [
            (x, x)
            for x in ICONS
        ]

    return []


# ---------------- IMAGE DELETION ----------------

def drop_file(name):
    """Delete an image from Supabase Storage and any old local copy."""

    if not name:
        return

    safe_name = os.path.basename(name)

    # Delete from Supabase Storage
    storage_client().storage.from_(
        STORAGE_BUCKET
    ).remove([safe_name])

    # Also remove an older local copy, if present
    path = os.path.join(UPLOADS, safe_name)

    if os.path.isfile(path):
        os.remove(path)


# ---------------- IMAGE UPLOAD ----------------

def save_image(fs):
    """Validate, orient, resize and upload an image to Supabase Storage."""

    try:

        im = Image.open(fs.stream)
        im.load()

    except Exception:
        return None

    im = ImageOps.exif_transpose(im)
    im.thumbnail((1200, 1200))

    alpha = im.mode in ("RGBA", "LA", "P")

    name = uuid.uuid4().hex + (
        ".png" if alpha else ".jpg"
    )

    buffer = io.BytesIO()

    if alpha:

        im.convert("RGBA").save(
            buffer,
            "PNG",
            optimize=True
        )

        content_type = "image/png"

    else:

        im.convert("RGB").save(
            buffer,
            "JPEG",
            quality=82,
            optimize=True
        )

        content_type = "image/jpeg"

    buffer.seek(0)

    # Upload image to Supabase Storage
    storage_client().storage.from_(
        STORAGE_BUCKET
    ).upload(
        name,
        buffer.getvalue(),
        file_options={
            "content-type": content_type,
            "cache-control": "3600",
            "upsert": "false"
        }
    )

    return name