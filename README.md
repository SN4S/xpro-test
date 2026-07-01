# Category & Product API

REST API для управління категоріями та товарами, побудований на **FastAPI** з **MySQL**.

## Технологічний стек

| Компонент | Технологія |
|-----------|-----------|
| Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (async) |
| База даних | MySQL 8.0 |
| Валідація | Pydantic v2 |
| Міграції | Alembic |
| Контейнеризація | Docker Compose |
| Reverse Proxy | Apache 2.4 |

## Швидкий старт

### 1. Клонувати репозиторій

```bash
git clone <url>
cd test
```

### 2. Запустити Docker

```bash
docker compose up -d --build
```

Це запустить 4 сервіси:

| Сервіс | URL | Опис |
|--------|-----|------|
| **FastAPI** | http://localhost:8000 | API сервер |
| **Swagger UI** | http://localhost:8000/docs | Інтерактивна документація API |
| **phpMyAdmin** | http://localhost:8080 | UI для управління базою даних |
| **Apache** | http://localhost:80 | Reverse proxy до FastAPI |

### 3. Заповнити демо-даними (seeder)

```bash
docker compose exec fastapi python -m src.seed
```

Це створить:
- **5** виробників (Alpinestars, Dainese, AGV, Shoei, Rev'It)
- **4** магазини
- **19** категорій (3 рівні вкладеності)
- **10** товарів з атрибутами, фото, категоріями та магазинами

> **Примітка:** Сідер скидає всі таблиці перед заповненням. Безпечно запускати повторно.

### 4. Перевірити роботу

```bash
# Health check
curl http://localhost:8000/

# Список категорій з повними шляхами
curl http://localhost:8000/category

# Деталі товару
curl http://localhost:8000/product/1
```

## Структура проекту

```
├── docker-compose.yml        # Docker сервіси
├── Dockerfile                # FastAPI контейнер
├── requirements.txt          # Python залежності
├── apache/
│   └── httpd.conf            # Apache reverse proxy
├── postman_collection.json   # Postman колекція для тестування
├── alembic.ini               # Конфігурація міграцій
├── migrations/               # Alembic міграції
└── src/
    ├── main.py               # FastAPI додаток
    ├── config.py             # Конфігурація
    ├── database.py           # Async SQLAlchemy
    ├── models.py             # Базова модель + TimestampMixin
    ├── exceptions.py         # HTTP виключення
    ├── seed.py               # Seeder з демо-даними
    ├── category/
    │   ├── models.py         # Модель категорії (самореференція)
    │   ├── schemas.py        # Pydantic схеми
    │   ├── service.py        # Бізнес-логіка
    │   ├── router.py         # Ендпоінти
    │   └── dependencies.py   # Залежності
    └── product/
        ├── models.py         # Product + 6 пов'язаних моделей
        ├── schemas.py        # Pydantic схеми
        ├── service.py        # CRUD операції
        ├── router.py         # 21 ендпоінт
        └── dependencies.py   # Залежності
```

## API ендпоінти

### Модуль «Категорії» (`/category`)

| Метод | Шлях | Опис |
|-------|------|------|
| `GET` | `/category` | Список категорій з повними шляхами, пагінацією, пошуком, фільтрацією, сортуванням |
| `GET` | `/category/{category_id}` | Всі дані категорії |
| `POST` | `/category` | Створення категорії (`parent_category_id=0` для кореневої) |
| `PATCH` | `/category/{category_id}` | Редагування (автоматично `date_modify`) |
| `DELETE` | `/category/{category_id}` | Рекурсивне видалення з підкатегоріями |

**Параметри `GET /category`:**

| Параметр | Тип | Опис |
|----------|-----|------|
| `page` | int | Номер сторінки (за замовчуванням 1) |
| `per_page` | int | Кількість на сторінці (за замовчуванням 20) |
| `search` | string | Пошук за назвою |
| `search_id` | int | Пошук за ID |
| `status` | int | Фільтр за статусом (1=Включена, 0=Виключена) |
| `sort_by` | string | Поле сортування: `name`, `category_id` |
| `sort_order` | string | Порядок: `asc` (А-Я), `desc` (Я-А) |

### Модуль «Товари» (`/product`)

| Метод | Шлях | Опис |
|-------|------|------|
| `GET` | `/product` | Список товарів з фільтрацією, сортуванням, пагінацією |
| `GET` | `/product/{product_id}` | Деталі товару (+ категорії, атрибути, фото, магазини, виробник) |
| `POST` | `/product` | Створення товару (приймає масиви категорій, атрибутів, фото) |
| `PATCH` | `/product/{product_id}` | Редагування (автоматично `date_modify`) |
| `DELETE` | `/product/{product_id}` | Видалення з усіма зв'язками |

**Підресурси товару:**

| Метод | Шлях | Опис |
|-------|------|------|
| `GET` | `/product/{id}/image` | Всі зображення товару |
| `GET` | `/product/{id}/image/{img_id}` | Конкретне зображення |
| `POST` | `/product/{id}/image` | Додати зображення |
| `PATCH` | `/product/{id}/image/{img_id}` | Змінити `sort_order` |
| `DELETE` | `/product/{id}/image/{img_id}` | Видалити зображення |
| `GET` | `/product/{id}/category` | Категорії товару (з назвами) |
| `GET` | `/product/{id}/category/{pc_id}` | Конкретна категорія товару |
| `POST` | `/product/{id}/category` | Додати категорію до товару |
| `DELETE` | `/product/{id}/category/{pc_id}` | Видалити категорію товару |
| `GET` | `/product/{id}/attribute` | Атрибути товару |
| `GET` | `/product/{id}/attribute/{attr_id}` | Конкретний атрибут |
| `POST` | `/product/{id}/attribute` | Додати атрибут |
| `PATCH` | `/product/{id}/attribute/{attr_id}` | Редагувати атрибут |
| `DELETE` | `/product/{id}/attribute/{attr_id}` | Видалити атрибут |
| `GET` | `/product/{id}/store` | Магазини товару |
| `GET` | `/product/{id}/store/{ps_id}` | Конкретний магазин товару |

## Тестування з Postman

1. Імпортуйте `postman_collection.json` у Postman
2. Колекція містить всі ендпоінти з прикладами тіл запитів
3. Базовий URL: `http://localhost:8000` (налаштовується через змінну `base_url`)

## Таблиці бази даних

| Таблиця | Опис |
|---------|------|
| `category` | Категорії з самореференцією (`parent_category_id`) |
| `product` | Товари |
| `product_category` | Зв'язок товар-категорія (унікальна пара) |
| `product_image` | Додаткові зображення товарів |
| `product_attribute` | Характеристики товарів |
| `manufacturer` | Виробники |
| `store` | Магазини |
| `product_store` | Зв'язок товар-магазин |

## Зупинити

```bash
docker compose down
```

Для повного очищення (включаючи дані MySQL):

```bash
docker compose down -v
```
