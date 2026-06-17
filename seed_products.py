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

products_to_add = [
    {
        "name": "iPhone 15 Pro Max",
        "list_price": 55000.0,
        "description_sale": "Brand: Apple. RAM: 8GB, Storage: 256GB, Processor: A17 Pro, Camera: 48MP Titanium, Battery: 4441mAh, Color: Natural Titanium. Premium flagship.",
    },
    {
        "name": "iPhone 14",
        "list_price": 32000.0,
        "description_sale": "Brand: Apple. RAM: 6GB, Storage: 128GB, Processor: A15 Bionic, Camera: 12MP Dual, Battery: 3279mAh, Color: Blue. Reliable iOS experience at lower cost.",
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "list_price": 52000.0,
        "description_sale": "Brand: Samsung. RAM: 12GB, Storage: 512GB, Processor: Snapdragon 8 Gen 3, Camera: 200MP, Battery: 5000mAh, Color: Titanium Gray. S-Pen Included. Ultimate Android.",
    },
    {
        "name": "Samsung Galaxy A36",
        "list_price": 15500.0,
        "description_sale": "Brand: Samsung. RAM: 8GB, Storage: 128GB, Processor: Snapdragon 6 Gen 1, Camera: 50MP, Battery: 5000mAh, Color: Black. Mid-range king.",
    },
    {
        "name": "Samsung Galaxy A15",
        "list_price": 7500.0,
        "description_sale": "Brand: Samsung. RAM: 4GB, Storage: 128GB, Processor: Helio G99, Camera: 50MP, Battery: 5000mAh, Color: Light Blue. Budget friendly option.",
    },
    {
        "name": "Redmi Note 14 Pro",
        "list_price": 14500.0,
        "description_sale": "Brand: Xiaomi. RAM: 12GB, Storage: 256GB, Processor: Dimensity 7300 Ultra, Camera: 50MP, Battery: 5500mAh, Color: Aurora Purple. Great value and battery life.",
    },
    {
        "name": "Xiaomi 14T Pro",
        "list_price": 29000.0,
        "description_sale": "Brand: Xiaomi. RAM: 12GB, Storage: 512GB, Processor: Dimensity 9300+, Camera: 50MP Leica Lens, Battery: 5000mAh, Color: Titan Black. Flagship killer.",
    },
    {
        "name": "Redmi 13C",
        "list_price": 6200.0,
        "description_sale": "Brand: Xiaomi. RAM: 6GB, Storage: 128GB, Processor: Helio G85, Camera: 50MP, Battery: 5000mAh, Color: Midnight Black. Entry level budget phone.",
    },
    {
        "name": "Realme GT 6T",
        "list_price": 18000.0,
        "description_sale": "Brand: Realme. RAM: 12GB, Storage: 256GB, Processor: Snapdragon 7+ Gen 3, Camera: 50MP, Battery: 5500mAh, Charging: 120W SuperVOOC, Color: Fluid Silver. Performance beast.",
    },
    {
        "name": "Realme C65",
        "list_price": 7800.0,
        "description_sale": "Brand: Realme. RAM: 8GB, Storage: 256GB, Processor: Helio G85, Camera: 50MP, Battery: 5000mAh, Charging: 45W, Color: Glowing Black. Solid budget choice.",
    },
    {
        "name": "Oppo Reno 12 Pro",
        "list_price": 21000.0,
        "description_sale": "Brand: Oppo. RAM: 12GB, Storage: 512GB, Processor: Dimensity 7300 Energy, Camera: 50MP + 50MP Telephoto, Battery: 5000mAh, Color: Space Brown. Excellent for portrait photography.",
    },
    {
        "name": "Oppo A60",
        "list_price": 9200.0,
        "description_sale": "Brand: Oppo. RAM: 8GB, Storage: 256GB, Processor: Snapdragon 680, Camera: 50MP, Battery: 5000mAh, Color: Ripple Blue. Military-grade shock resistance.",
    },
    {
        "name": "Honor 200",
        "list_price": 19500.0,
        "description_sale": "Brand: Honor. RAM: 12GB, Storage: 256GB, Processor: Snapdragon 7 Gen 3, Camera: 50MP Studio Portrait, Battery: 5200mAh, Color: Emerald Green. Premium design.",
    },
    {
        "name": "Honor X8b",
        "list_price": 11000.0,
        "description_sale": "Brand: Honor. RAM: 8GB, Storage: 512GB, Processor: Snapdragon 680, Camera: 108MP, Battery: 4500mAh, Color: Glamorous Green. Huge storage.",
    },
    {
        "name": "Vivo V40",
        "list_price": 23500.0,
        "description_sale": "Brand: Vivo. RAM: 12GB, Storage: 256GB, Processor: Snapdragon 7 Gen 3, Camera: 50MP Zeiss Optics, Battery: 5500mAh, Color: Stellar Silver. Professional camera tuning.",
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

        # بنرمي الكمية الحقيقية علطول في المخزن بدون استدعاء ميثود الـ Apply المزعجة لسيرفر الـ RPC
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