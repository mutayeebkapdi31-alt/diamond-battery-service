from models import db, rows, ENT
SERVICES = [
 ("Car batteries","bat","All types of car batteries.","Battery testing\nSales of branded batteries\nFitting and terminal check"),
 ("Inverter & UPS","inv","Inverter and UPS batteries and systems.","For home and shop use\nSales and installation\nBackup power you can rely on"),
 ("Car scanning","scan","Computer scanning for all types of cars.","Reads fault codes\nFinds the problem before parts are replaced\nAll major car brands"),
 ("ECM repairing & programming","ecm","Engine control module repair and programming.","ECM fault repair\nProgramming\nFewer unnecessary part changes"),
 ("Armature","arm","Sales, rewinding and repairing.","Armature sales\nRewinding\nRepairing"),
 ("Starter","start","Starter motor sales, rewinding and repairing.","Starter sales\nRewinding\nRepairing"),
 ("Alternator","alt","Alternator sales, rewinding and repairing.","Alternator sales\nRewinding\nRepairing"),
 ("Car A/C service & repairing","ac","Complete car A/C servicing and repair.","A/C checkup\nRepair of A/C faults\nBetter cooling in summer"),
 ("A/C gas filling","gas","Car A/C gas filling.","Gas top-up and refill\nCooling check after filling\nQuick service")]
BRANDS = ["Amaron","Exide","SF Sonic","Luminous","Su-Kam"]
CATS = [("2 Wheeler","2","Wheeler","Bikes and scooters"),("4 Wheeler","4","Wheeler","Cars, SUVs and vans")] + \
  [(f"{n} Wheeler",str(n),"Wheeler","") for n in (6,8,10,12,14,16,18,20)] + [("Home Inverter & UPS","Home","Inverter","Homes, shops and offices")]
TYPES = [("Car & SUV batteries","bat","Starting batteries for four wheelers."),("Two-wheeler batteries","bat","Batteries for bikes and scooters."),
 ("Commercial & heavy vehicle batteries","bat","For 6 wheelers up to 20 wheelers."),("Home inverter: tubular","inv","Tubular batteries for home inverters."),
 ("Home inverter: flat plate","inv","Flat plate batteries for home inverters."),("UPS & other batteries","inv","Ask us for any other battery you need.")]
WARR = [("shield","Brand warranty on batteries","Branded batteries such as Amaron, Exide, SF Sonic, Luminous and Su-Kam come with the manufacturer's warranty."),
 ("doc","Warranty card & bill","Ask for your warranty card and purchase bill when you buy, and keep them safe for any future claim."),
 ("wrench","Repair work assurance","Ask us about the guarantee on repair and rewinding work for your starter, alternator, armature or ECM."),
 ("scan","Tested before you pay","We test and scan first so you only replace what is actually faulty.")]
SIGNS = [("Slow or weak starting","Often a weak battery or a worn starter.","bat","Car batteries"),("Dim headlights","Can point to the battery or the alternator not charging.","alt","Alternator"),
 ("Clicking sound when starting","Usually a flat battery or a starter fault.","start","Starter"),("Battery or warning light on","The charging system needs checking.","scan","Car scanning"),
 ("Check engine light","A scan finds the fault code and the cause.","ecm","ECM repairing & programming"),("A/C blowing warm air","May need an A/C check or gas filling.","ac","Car A/C service & repairing")]
FAQS = [("How long does a car battery last?","Most car batteries last a few years, but heat, short trips, driving habits and the electrical load all affect life. A quick test tells you where yours stands."),
 ("Is it the battery or the alternator?","A weak battery struggles to start the car, while a faulty alternator stops the battery from charging while you drive. We test both so you do not replace the wrong part."),
 ("What is an ECM and why would it need repair?","The ECM (engine control module) is the computer that manages your engine. When it fails you can see warning lights, poor running or no start. We repair and program ECMs."),
 ("Why does my car need computer scanning?","A scanner reads the fault codes stored by the car, which shows where the problem is and saves time and money on guesswork."),
 ("Which cars do you work on?","Maruti Suzuki, Hyundai, Chevrolet, Nissan, Volkswagen, Skoda, Toyota, Ford, Tata and Mahindra."),
 ("What warranty do I get?","Batteries carry the brand's own warranty. The period depends on the brand and model, so please ask us before buying and keep your warranty card and bill."),
 ("How do I book a service?","Call or WhatsApp us, or send the booking form on this page and we will call you back.")]
REVIEWS = ["My car died at night near Murbad. They fixed it quickly and fairly.","Honest pricing. My alternator problem was solved the same day.","Best place in Murbad for batteries and A/C gas filling."]
STATS = [(9,"services under one roof"),(10,"car brands serviced"),(5,"battery brands stocked"),(2,"phone lines to reach us")]
# (brand index, type, category labels)
PROD = [(0,"Car & SUV",["4 Wheeler"]),(0,"Two-wheeler",["2 Wheeler"]),(0,"Commercial & heavy vehicle",["6","8","10","12","14","16","18","20"]),
 (1,"Car & SUV",["4 Wheeler"]),(1,"Two-wheeler",["2 Wheeler"]),(1,"Commercial & heavy vehicle",["6","8","10","12","14","16","18","20"]),
 (1,"Home inverter battery",["Home Inverter & UPS"]),(2,"Car & SUV",["4 Wheeler"]),(2,"Commercial & heavy vehicle",["6","8","10","12","14","16","18","20"]),
 (3,"Home inverter: tubular",["Home Inverter & UPS"]),(3,"Home inverter: flat plate",["Home Inverter & UPS"]),(4,"Inverter & UPS",["Home Inverter & UPS"])]

def run():
    with db() as c:

        # Prevent duplicate initial data
        service_count = c.execute(
            "SELECT COUNT(*) AS total FROM services"
        ).fetchone()["total"]

        brand_count = c.execute(
            "SELECT COUNT(*) AS total FROM brands"
        ).fetchone()["total"]

        if service_count or brand_count:
            print("Initial website content already exists. Skipping seed.")
            return

        # Services
        for i, s in enumerate(SERVICES, 1):
            c.execute("""
                INSERT INTO services
                (title, icon, descr, items, sort, active)
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (s[0], s[1], s[2], s[3], i))

        # Brands
        for i, b in enumerate(BRANDS, 1):
            c.execute("""
                INSERT INTO brands (name, sort, active)
                VALUES (%s, %s, 1)
            """, (b, i))

        # Vehicle categories
        for i, x in enumerate(CATS, 1):
            c.execute("""
                INSERT INTO categories
                (label, short, sub, descr, sort, active)
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (*x, i))

        # Battery types
        for i, x in enumerate(TYPES, 1):
            c.execute("""
                INSERT INTO types
                (title, icon, descr, sort, active)
                VALUES (%s, %s, %s, %s, 1)
            """, (*x, i))

        # Warranties
        for i, x in enumerate(WARR, 1):
            c.execute("""
                INSERT INTO warranties
                (icon, title, descr, sort, active)
                VALUES (%s, %s, %s, %s, 1)
            """, (*x, i))

        # Warning signs
        for i, x in enumerate(SIGNS, 1):
            c.execute("""
                INSERT INTO signs
                (title, descr, icon, service, sort, active)
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (*x, i))

        # FAQs
        for i, x in enumerate(FAQS, 1):
            c.execute("""
                INSERT INTO faqs (q, a, sort, active)
                VALUES (%s, %s, %s, 1)
            """, (*x, i))

        # Sample reviews
        for i, x in enumerate(REVIEWS, 1):
            c.execute("""
                INSERT INTO reviews (text, author, sort, active)
                VALUES (%s, %s, %s, 1)
            """, (x, "Sample review: replace with a real customer", i))

        # Website highlights
        for i, x in enumerate(STATS, 1):
            c.execute("""
                INSERT INTO stats (number, label, sort, active)
                VALUES (%s, %s, %s, 1)
            """, (*x, i))

        # Get inserted brand IDs
        brand_rows = c.execute(
            "SELECT id, name FROM brands"
        ).fetchall()

        brand_ids = {
            r["name"]: r["id"] for r in brand_rows
        }

        # Get inserted category IDs
        category_rows = c.execute(
            "SELECT id, label, short FROM categories"
        ).fetchall()

        category_ids = {}

        for r in category_rows:
            category_ids[r["label"]] = str(r["id"])
            category_ids[r["short"]] = str(r["id"])

        # Products
        for i, (brand_index, battery_type, categories) in enumerate(PROD, 1):

            brand_name = BRANDS[brand_index]
            brand_id = brand_ids[brand_name]

            selected_ids = []

            for category in categories:
                category_id = category_ids.get(category)

                if category_id and category_id not in selected_ids:
                    selected_ids.append(category_id)

            if not selected_ids:
                raise ValueError(
                    f"No matching vehicle category found for {battery_type}"
                )

            cats_value = ",".join(selected_ids)

            c.execute("""
                INSERT INTO products
                (brand, type, cats, sort, active)
                VALUES (%s, %s, %s, %s, 1)
            """, (
                str(brand_id),
                battery_type,
                cats_value,
                i
            ))

    print("Diamond Battery Service initial content seeded successfully!")