"""
Database seeder with demo data for Category & Product API.

Run: docker compose exec fastapi python -m src.seed
"""

import asyncio
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import engine, SessionFactory
from src.models import Base

# Import all models
from src.category.models import Category
from src.product.models import (
    Manufacturer,
    Product,
    ProductAttribute,
    ProductCategory,
    ProductImage,
    ProductStore,
    Store,
)


async def seed():
    """Seed the database with demo data."""

    # Recreate all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionFactory() as db:
        print("Seeding manufacturers...")
        manufacturers = await seed_manufacturers(db)

        print("Seeding stores...")
        stores = await seed_stores(db)

        print("Seeding categories...")
        categories = await seed_categories(db)

        print("Seeding products...")
        await seed_products(db, categories, manufacturers, stores)

        print("\n=== Seed complete! ===")
        print(f"  Manufacturers: {len(manufacturers)}")
        print(f"  Stores:        {len(stores)}")
        print(f"  Categories:    {len(categories)}")
        print("  Products:      10")
        print("\nAPI: http://localhost:8000")
        print("Docs: http://localhost:8000/docs")


async def seed_manufacturers(db: AsyncSession) -> list[Manufacturer]:
    items = [
        Manufacturer(name="Alpinestars"),
        Manufacturer(name="Dainese"),
        Manufacturer(name="AGV"),
        Manufacturer(name="Shoei"),
        Manufacturer(name="Rev'It"),
    ]
    db.add_all(items)
    await db.commit()
    for m in items:
        await db.refresh(m)
    return items


async def seed_stores(db: AsyncSession) -> list[Store]:
    items = [
        Store(name="Головний магазин (Київ)"),
        Store(name="Філія Львів"),
        Store(name="Філія Одеса"),
        Store(name="Онлайн-магазин"),
    ]
    db.add_all(items)
    await db.commit()
    for s in items:
        await db.refresh(s)
    return items


async def seed_categories(db: AsyncSession) -> dict[str, Category]:
    """Create a hierarchical category tree and return a name->Category map."""

    cats: dict[str, Category] = {}

    # === Root categories ===
    c_rider = Category(name="Для мотоцикліста", status=1,
                       seo_keyword="dlya-motocyklista",
                       meta_title="Для мотоцикліста — все для райдера",
                       description="Екіпіровка, аксесуари та взуття для мотоциклістів")
    c_bike = Category(name="Для мотоцикла", status=1,
                      seo_keyword="dlya-motocykla",
                      meta_title="Для мотоцикла — запчастини та аксесуари",
                      description="Все для вашого мотоцикла")
    c_sale = Category(name="Розпродаж", status=1,
                      seo_keyword="rozprodazh",
                      meta_title="Розпродаж — знижки до 70%")

    db.add_all([c_rider, c_bike, c_sale])
    await db.flush()

    # === Для мотоцикліста > children ===
    c_accessories = Category(name="Аксесуари", parent_category_id=c_rider.category_id, status=1,
                             seo_keyword="aksesuari")
    c_bestsellers = Category(name="Бестселери", parent_category_id=c_rider.category_id, status=1,
                             seo_keyword="bestsellery")
    c_shoes = Category(name="Взуття", parent_category_id=c_rider.category_id, status=1,
                       seo_keyword="vzuttya")
    c_helmets = Category(name="Шоломи", parent_category_id=c_rider.category_id, status=1,
                         seo_keyword="sholomy")
    c_jackets = Category(name="Куртки", parent_category_id=c_rider.category_id, status=1,
                         seo_keyword="kurtky")

    db.add_all([c_accessories, c_bestsellers, c_shoes, c_helmets, c_jackets])
    await db.flush()

    # === Аксесуари > grandchildren ===
    c_backpacks = Category(name="Рюкзаки", parent_category_id=c_accessories.category_id, status=1,
                           seo_keyword="ryukzaky")
    c_balaclavas = Category(name="Балаклави та коміри", parent_category_id=c_accessories.category_id, status=1,
                            seo_keyword="balaklavy")
    c_knee_pads = Category(name="Накладки на коліна", parent_category_id=c_accessories.category_id, status=1,
                           seo_keyword="nakladky-na-kolina")
    c_gloves = Category(name="Рукавиці", parent_category_id=c_accessories.category_id, status=1,
                        seo_keyword="rukavytsi")

    db.add_all([c_backpacks, c_balaclavas, c_knee_pads, c_gloves])
    await db.flush()

    # === Взуття > grandchildren ===
    c_short_boots = Category(name="Короткі", parent_category_id=c_shoes.category_id, status=1,
                             seo_keyword="korotki-boty")
    c_adventure = Category(name="Пригоди", parent_category_id=c_shoes.category_id, status=1,
                           seo_keyword="prygody-boty")
    c_sport_boots = Category(name="Спортивні", parent_category_id=c_shoes.category_id, status=1,
                             seo_keyword="sportyvni-boty")

    db.add_all([c_short_boots, c_adventure, c_sport_boots])
    await db.flush()

    # === Для мотоцикла > children ===
    c_exhaust = Category(name="Вихлопні системи", parent_category_id=c_bike.category_id, status=1,
                         seo_keyword="vykhlopni-systemy")
    c_protection = Category(name="Захист", parent_category_id=c_bike.category_id, status=1,
                            seo_keyword="zakhyst")
    c_lighting = Category(name="Освітлення", parent_category_id=c_bike.category_id, status=1,
                          seo_keyword="osvitlennya")
    c_disabled = Category(name="Старий каталог", parent_category_id=c_bike.category_id, status=0,
                          seo_keyword="staryj-katalog")

    db.add_all([c_exhaust, c_protection, c_lighting, c_disabled])
    await db.commit()

    # Refresh all and build map
    all_cats = [c_rider, c_bike, c_sale, c_accessories, c_bestsellers, c_shoes,
                c_helmets, c_jackets, c_backpacks, c_balaclavas, c_knee_pads,
                c_gloves, c_short_boots, c_adventure, c_sport_boots,
                c_exhaust, c_protection, c_lighting, c_disabled]
    for c in all_cats:
        await db.refresh(c)
        cats[c.name] = c

    return cats


async def seed_products(
    db: AsyncSession,
    cats: dict[str, Category],
    manufacturers: list[Manufacturer],
    stores: list[Store],
):
    """Create 10 products with categories, attributes, images, and store links."""

    alpinestars, dainese, agv, shoei, revit = manufacturers
    store_kyiv, store_lviv, store_odesa, store_online = stores

    products_data = [
        {
            "product": Product(
                name="Alpinestars Tech-Air 5 Airbag System",
                description="Автономна система подушки безпеки для мотоциклістів. Захищає спину, грудну клітку та плечі.",
                price=29999.00, model="TECH-AIR-5", status=1,
                manufacturer_id=alpinestars.manufacturer_id,
                rating=4.8, viewed=1250,
                seo_keyword="alpinestars-tech-air-5",
                meta_title="Alpinestars Tech-Air 5 — купити Airbag систему",
                image="/uploads/products/tech-air-5-main.jpg",
            ),
            "categories": ["Куртки", "Бестселери"],
            "attributes": [
                ("Загальне", "Бренд", "Alpinestars", 0),
                ("Загальне", "Країна", "Італія", 1),
                ("Характеристики", "Час спрацювання", "< 50 мс", 2),
                ("Характеристики", "Вага", "1.7 кг", 3),
                ("Розміри", "Розміри", "S, M, L, XL, XXL", 4),
            ],
            "images": [
                ("/uploads/products/tech-air-5-front.jpg", 0),
                ("/uploads/products/tech-air-5-back.jpg", 1),
                ("/uploads/products/tech-air-5-side.jpg", 2),
            ],
            "stores": [store_kyiv, store_online],
        },
        {
            "product": Product(
                name="Dainese Torque 3 Out Boots",
                description="Професійні спортивні мотоботи з магнієвим слайдером.",
                price=12500.00, model="TORQUE-3-OUT", status=1,
                manufacturer_id=dainese.manufacturer_id,
                rating=4.6, viewed=890,
                seo_keyword="dainese-torque-3-out",
                image="/uploads/products/torque-3-main.jpg",
            ),
            "categories": ["Спортивні", "Взуття"],
            "attributes": [
                ("Загальне", "Бренд", "Dainese", 0),
                ("Характеристики", "Матеріал", "Натуральна шкіра D-Stone", 1),
                ("Характеристики", "Захист", "CE Level 2", 2),
                ("Розміри", "Розміри", "39-47", 3),
            ],
            "images": [
                ("/uploads/products/torque-3-left.jpg", 0),
                ("/uploads/products/torque-3-right.jpg", 1),
            ],
            "stores": [store_kyiv, store_lviv, store_online],
        },
        {
            "product": Product(
                name="AGV Pista GP RR Шолом",
                description="Топовий гоночний шолом з карбоновою оболонкою. Використовується у MotoGP.",
                price=45000.00, model="PISTA-GP-RR", status=1,
                manufacturer_id=agv.manufacturer_id,
                rating=4.9, viewed=2100,
                seo_keyword="agv-pista-gp-rr",
                image="/uploads/products/pista-gp-rr-main.jpg",
            ),
            "categories": ["Шоломи", "Бестселери"],
            "attributes": [
                ("Загальне", "Бренд", "AGV", 0),
                ("Характеристики", "Матеріал оболонки", "100% Carbon Fiber", 1),
                ("Характеристики", "Вага", "1350 г (±50)", 2),
                ("Характеристики", "Сертифікація", "ECE 22.06, FIM", 3),
                ("Вентиляція", "Канали", "5 передніх, 2 задніх", 4),
            ],
            "images": [
                ("/uploads/products/pista-gp-rr-front.jpg", 0),
                ("/uploads/products/pista-gp-rr-visor.jpg", 1),
                ("/uploads/products/pista-gp-rr-interior.jpg", 2),
            ],
            "stores": [store_kyiv, store_online],
        },
        {
            "product": Product(
                name="Rev'It Sand 4 H2O Куртка",
                description="Туристична куртка з водонепроникною мембраною Hydratex для пригод.",
                price=15800.00, model="SAND-4-H2O", status=1,
                manufacturer_id=revit.manufacturer_id,
                rating=4.5, viewed=670,
                seo_keyword="revit-sand-4-h2o",
                image="/uploads/products/sand-4-main.jpg",
            ),
            "categories": ["Куртки"],
            "attributes": [
                ("Загальне", "Бренд", "Rev'It", 0),
                ("Характеристики", "Мембрана", "Hydratex Lite", 1),
                ("Характеристики", "Захист", "SEESMART CE Level 2 (плечі, лікті)", 2),
                ("Характеристики", "Сезон", "Всесезонна", 3),
            ],
            "images": [
                ("/uploads/products/sand-4-front.jpg", 0),
                ("/uploads/products/sand-4-back.jpg", 1),
            ],
            "stores": [store_kyiv, store_lviv, store_odesa, store_online],
        },
        {
            "product": Product(
                name="Dainese Full Metal 7 Рукавиці",
                description="Гоночні рукавиці з титановими та карбоновими протекторами.",
                price=11200.00, model="FULL-METAL-7", status=1,
                manufacturer_id=dainese.manufacturer_id,
                rating=4.7, viewed=430,
                seo_keyword="dainese-full-metal-7",
                image="/uploads/products/full-metal-7-main.jpg",
            ),
            "categories": ["Рукавиці", "Бестселери"],
            "attributes": [
                ("Загальне", "Бренд", "Dainese", 0),
                ("Характеристики", "Матеріал", "Козяча шкіра + Kangoo", 1),
                ("Характеристики", "Протектори", "Титан + карбон", 2),
                ("Розміри", "Розміри", "XS-XXL", 3),
            ],
            "images": [
                ("/uploads/products/full-metal-7-palm.jpg", 0),
                ("/uploads/products/full-metal-7-top.jpg", 1),
            ],
            "stores": [store_kyiv, store_online],
        },
        {
            "product": Product(
                name="Alpinestars Supertech R Boots",
                description="Гоночні мотоботи з внутрішнім каркасом та підвищеним рівнем захисту.",
                price=18500.00, model="SUPERTECH-R", status=1,
                manufacturer_id=alpinestars.manufacturer_id,
                rating=4.7, viewed=780,
                seo_keyword="alpinestars-supertech-r",
                image="/uploads/products/supertech-r-main.jpg",
            ),
            "categories": ["Спортивні", "Взуття"],
            "attributes": [
                ("Загальне", "Бренд", "Alpinestars", 0),
                ("Характеристики", "Захист", "CE Level 2", 1),
                ("Розміри", "Розміри", "38-48", 2),
            ],
            "images": [
                ("/uploads/products/supertech-r-side.jpg", 0),
            ],
            "stores": [store_kyiv, store_lviv, store_online],
        },
        {
            "product": Product(
                name="Мотоциклетний рюкзак Kriega R20",
                description="Компактний рюкзак на 20 літрів з системою Quadloc-lite.",
                price=5600.00, model="KRIEGA-R20", status=1,
                rating=4.4, viewed=320,
                seo_keyword="kriega-r20",
                image="/uploads/products/kriega-r20-main.jpg",
            ),
            "categories": ["Рюкзаки", "Аксесуари"],
            "attributes": [
                ("Загальне", "Бренд", "Kriega", 0),
                ("Характеристики", "Об'єм", "20 л", 1),
                ("Характеристики", "Матеріал", "Cordura 1000D", 2),
                ("Характеристики", "Водонепроникність", "Так", 3),
            ],
            "images": [
                ("/uploads/products/kriega-r20-open.jpg", 0),
                ("/uploads/products/kriega-r20-on-rider.jpg", 1),
            ],
            "stores": [store_online],
        },
        {
            "product": Product(
                name="Shoei NXR 2 Шолом",
                description="Інтегральний спортивно-туристичний шолом з покращеною аеродинамікою.",
                price=22000.00, model="NXR-2", status=1,
                manufacturer_id=shoei.manufacturer_id,
                rating=4.6, viewed=560,
                seo_keyword="shoei-nxr-2",
                image="/uploads/products/nxr-2-main.jpg",
            ),
            "categories": ["Шоломи"],
            "attributes": [
                ("Загальне", "Бренд", "Shoei", 0),
                ("Характеристики", "Матеріал оболонки", "AIM+", 1),
                ("Характеристики", "Вага", "1380 г (±50)", 2),
                ("Характеристики", "Сертифікація", "ECE 22.06", 3),
            ],
            "images": [
                ("/uploads/products/nxr-2-side.jpg", 0),
            ],
            "stores": [store_kyiv, store_odesa, store_online],
        },
        {
            "product": Product(
                name="Балаклава Dainese D-Core Balaclava",
                description="Термобалаклава з безшовною конструкцією для носіння під шоломом.",
                price=1200.00, model="D-CORE-BALA", status=1,
                manufacturer_id=dainese.manufacturer_id,
                rating=4.2, viewed=150,
                seo_keyword="dainese-d-core-balaclava",
                image="/uploads/products/d-core-bala-main.jpg",
            ),
            "categories": ["Балаклави та коміри"],
            "attributes": [
                ("Загальне", "Бренд", "Dainese", 0),
                ("Характеристики", "Матеріал", "Dryarn + Polypropylene", 1),
                ("Розміри", "Розміри", "One Size", 2),
            ],
            "images": [],
            "stores": [store_kyiv, store_lviv, store_odesa, store_online],
        },
        {
            "product": Product(
                name="Короткі мотоботи TCX Street 3 WP",
                description="Міські водонепроникні мотоботи з прихованим захистом.",
                price=6800.00, model="STREET-3-WP", status=0,
                rating=4.3, viewed=210,
                seo_keyword="tcx-street-3-wp",
                image="/uploads/products/street-3-wp-main.jpg",
            ),
            "categories": ["Короткі"],
            "attributes": [
                ("Загальне", "Бренд", "TCX", 0),
                ("Характеристики", "Мембрана", "T-Dry", 1),
                ("Характеристики", "Захист", "CE Level 2", 2),
            ],
            "images": [
                ("/uploads/products/street-3-wp-pair.jpg", 0),
            ],
            "stores": [store_online],
        },
    ]

    for item in products_data:
        product = item["product"]
        db.add(product)
        await db.flush()

        # Add categories
        for cat_name in item["categories"]:
            if cat_name in cats:
                pc = ProductCategory(
                    product_id=product.product_id,
                    category_id=cats[cat_name].category_id,
                )
                db.add(pc)

        # Add attributes
        for group, name, value, sort in item["attributes"]:
            attr = ProductAttribute(
                product_id=product.product_id,
                group_name=group, name=name, value=value, sort_order=sort,
            )
            db.add(attr)

        # Add images
        for img_path, sort in item["images"]:
            img = ProductImage(
                product_id=product.product_id,
                image=img_path, sort_order=sort,
            )
            db.add(img)

        # Add stores
        for store in item["stores"]:
            ps = ProductStore(
                product_id=product.product_id,
                store_id=store.store_id,
            )
            db.add(ps)

    await db.commit()
    print(f"  Created {len(products_data)} products with relations")


if __name__ == "__main__":
    asyncio.run(seed())
