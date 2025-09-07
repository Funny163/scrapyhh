# Alkoteka Scraper

Scrapy паук для сбора товаров с сайта Alkoteka.  
Парсер обходит категории, получает товары через API `/v1/product` и сохраняет результат в `result.json`.

---

## Содержание проекта

- `myproject/` — Scrapy проект  
- `myproject/spiders/spider_name.py` — основной паук  
- `myproject/parsers/product_parser.py` — модуль обработки JSON товаров  
- `myproject/middlewares.py` — прокси и Random User-Agent  
- `proxy.txt` — файл для прокси  
- `requirements.txt` — зависимости проекта  
- `.gitignore` — игнорируемые файлы  

---

## Быстрый старт

### 1. Клонирование
```
git clone https://github.com/Funny163/scrapyhh.git
cd scrapyhh
```

### 2.Создание и активация виртуального окружения

#### Windows (PowerShell):

```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### Windows (cmd):

```
python -m venv .venv
.venv\Scripts\activate.bat
```

#### macOS / Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```
### 3. Установка зависимостей
```
pip install -r requirements.txt
```

### 4. Настройка прокси

Откройте файл proxy.txt рядом со scrapy.cfg.

Формат строк в файле:

```
http://USERNAME:PASSWORD@IP:PORT
https://USERNAME:PASSWORD@IP:PORT
https://IP:PORT
```

Комментарии начинаются с "#".

### 5. Настройка категорий для парсинга

Список категорий находится в файле `spiders/spider_name.py` в переменной `START_URLS`:

```python
START_URLS = [
    'https://alkoteka.com/catalog/slaboalkogolnye-napitki-2',
    'https://alkoteka.com/catalog/krepkiy-alkogol',
]
```

- Чтобы добавить категорию, просто добавьте новый URL в список.
- Чтобы изменить категорию, замените URL на нужный.


### 6. Запуск паука
```
scrapy crawl spider_name -O result.json
```
