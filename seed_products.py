import xmlrpc.client

URL = "http://localhost:8069"
DB = "mobile_store_ai"
USERNAME = "admin"
PASSWORD = "admin"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})

if not uid:
    print("Authentication failed.")
    exit()

print(f"Connected successfully. User ID: {uid}")
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

# Ensure brands exist
BRANDS = {
    "Apple": "APPLE",
    "Samsung": "SAMSUNG",
    "Xiaomi": "XIAOMI",
    "Realme": "REALME",
    "Oppo": "OPPO",
    "Honor": "HONOR",
    "Vivo": "VIVO",
}

brand_ids = {}
for brand_name, brand_code in BRANDS.items():
    existing = models.execute_kw(
        DB, uid, PASSWORD, "product.brand", "search", [[["code", "=", brand_code]]]
    )
    if existing:
        brand_ids[brand_name] = existing[0]
        print(f"Found brand: {brand_name} (ID: {existing[0]})")
    else:
        bid = models.execute_kw(
            DB, uid, PASSWORD, "product.brand", "create", [{"name": brand_name, "code": brand_code}]
        )
        brand_ids[brand_name] = bid
        print(f"Created brand: {brand_name} (ID: {bid})")

products_to_add = [
    {
        "name": "iPhone 15 Pro Max",
        "list_price": 55000.0,
        "brand": "Apple",
        "ram": "8GB",
        "storage": "256GB",
        "processor": "A17 Pro",
        "camera": "48MP Titanium",
        "battery": "4441mAh",
        "color": "Natural Titanium",
        "description_sale": "Premium flagship with titanium design.",
    },
    {
        "name": "iPhone 14",
        "list_price": 32000.0,
        "brand": "Apple",
        "ram": "6GB",
        "storage": "128GB",
        "processor": "A15 Bionic",
        "camera": "12MP Dual",
        "battery": "3279mAh",
        "color": "Blue",
        "description_sale": "Reliable iOS experience at lower cost.",
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "list_price": 52000.0,
        "brand": "Samsung",
        "ram": "12GB",
        "storage": "512GB",
        "processor": "Snapdragon 8 Gen 3",
        "camera": "200MP",
        "battery": "5000mAh",
        "color": "Titanium Gray",
        "description_sale": "S-Pen Included. Ultimate Android flagship.",
    },
    {
        "name": "Samsung Galaxy A36",
        "list_price": 15500.0,
        "brand": "Samsung",
        "ram": "8GB",
        "storage": "128GB",
        "processor": "Snapdragon 6 Gen 1",
        "camera": "50MP",
        "battery": "5000mAh",
        "color": "Black",
        "description_sale": "Mid-range king with great value.",
    },
    {
        "name": "Samsung Galaxy A15",
        "list_price": 7500.0,
        "brand": "Samsung",
        "ram": "4GB",
        "storage": "128GB",
        "processor": "Helio G99",
        "camera": "50MP",
        "battery": "5000mAh",
        "color": "Light Blue",
        "description_sale": "Budget friendly option.",
    },
    {
        "name": "Redmi Note 14 Pro",
        "list_price": 14500.0,
        "brand": "Xiaomi",
        "ram": "12GB",
        "storage": "256GB",
        "processor": "Dimensity 7300 Ultra",
        "camera": "50MP",
        "battery": "5500mAh",
        "color": "Aurora Purple",
        "description_sale": "Great value and battery life.",
    },
    {
        "name": "Xiaomi 14T Pro",
        "list_price": 29000.0,
        "brand": "Xiaomi",
        "ram": "12GB",
        "storage": "512GB",
        "processor": "Dimensity 9300+",
        "camera": "50MP Leica Lens",
        "battery": "5000mAh",
        "color": "Titan Black",
        "description_sale": "Flagship killer with Leica optics.",
    },
    {
        "name": "Redmi 13C",
        "list_price": 6200.0,
        "brand": "Xiaomi",
        "ram": "6GB",
        "storage": "128GB",
        "processor": "Helio G85",
        "camera": "50MP",
        "battery": "5000mAh",
        "color": "Midnight Black",
        "description_sale": "Entry level budget phone.",
    },
    {
        "name": "Realme GT 6T",
        "list_price": 18000.0,
        "brand": "Realme",
        "ram": "12GB",
        "storage": "256GB",
        "processor": "Snapdragon 7+ Gen 3",
        "camera": "50MP",
        "battery": "5500mAh",
        "color": "Fluid Silver",
        "description_sale": "Performance beast with 120W SuperVOOC charging.",
    },
    {
        "name": "Realme C65",
        "list_price": 7800.0,
        "brand": "Realme",
        "ram": "8GB",
        "storage": "256GB",
        "processor": "Helio G85",
        "camera": "50MP",
        "battery": "5000mAh",
        "color": "Glowing Black",
        "description_sale": "Solid budget choice with 45W charging.",
    },
    {
        "name": "Oppo Reno 12 Pro",
        "list_price": 21000.0,
        "brand": "Oppo",
        "ram": "12GB",
        "storage": "512GB",
        "processor": "Dimensity 7300 Energy",
        "camera": "50MP + 50MP Telephoto",
        "battery": "5000mAh",
        "color": "Space Brown",
        "description_sale": "Excellent for portrait photography.",
    },
    {
        "name": "Oppo A60",
        "list_price": 9200.0,
        "brand": "Oppo",
        "ram": "8GB",
        "storage": "256GB",
        "processor": "Snapdragon 680",
        "camera": "50MP",
        "battery": "5000mAh",
        "color": "Ripple Blue",
        "description_sale": "Military-grade shock resistance.",
    },
    {
        "name": "Honor 200",
        "list_price": 19500.0,
        "brand": "Honor",
        "ram": "12GB",
        "storage": "256GB",
        "processor": "Snapdragon 7 Gen 3",
        "camera": "50MP Studio Portrait",
        "battery": "5200mAh",
        "color": "Emerald Green",
        "description_sale": "Premium design with studio portrait camera.",
    },
    {
        "name": "Honor X8b",
        "list_price": 11000.0,
        "brand": "Honor",
        "ram": "8GB",
        "storage": "512GB",
        "processor": "Snapdragon 680",
        "camera": "108MP",
        "battery": "4500mAh",
        "color": "Glamorous Green",
        "description_sale": "Huge storage with 108MP camera.",
    },
    {
        "name": "Vivo V40",
        "list_price": 23500.0,
        "brand": "Vivo",
        "ram": "12GB",
        "storage": "256GB",
        "processor": "Snapdragon 7 Gen 3",
        "camera": "50MP Zeiss Optics",
        "battery": "5500mAh",
        "color": "Stellar Silver",
        "description_sale": "Professional camera tuning with Zeiss optics.",
    },
]

location_ids = models.execute_kw(
    DB, uid, PASSWORD, "stock.location", "search", [[["usage", "=", "internal"]]]
)
default_location = location_ids[0] if location_ids else 8

for prod in products_to_add:
    product_id = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "product.template",
        "create",
        [
            {
                "name": prod["name"],
                "list_price": prod["list_price"],
                "description_sale": prod["description_sale"],
                "detailed_type": "product",
                "invoice_policy": "order",
                "brand_id": brand_ids.get(prod["brand"]),
                "ram": prod.get("ram"),
                "storage": prod.get("storage"),
                "processor": prod.get("processor"),
                "camera": prod.get("camera"),
                "battery": prod.get("battery"),
                "color": prod.get("color"),
            }
        ],
    )
    print(f"Created: {prod['name']} (ID: {product_id})")

    product_product_ids = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "product.product",
        "search",
        [[["product_tmpl_id", "=", product_id]]],
    )

    if product_product_ids:
        p_id = product_product_ids[0]
        qty = 12 if "Max" in prod["name"] or "Ultra" in prod["name"] else 20

        models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "stock.quant",
            "create",
            [
                {
                    "product_id": p_id,
                    "location_id": default_location,
                    "quantity": qty,
                }
            ],
        )
        print(f"Stock updated for {prod['name']}: +{qty}")

print("Migration completed.")
