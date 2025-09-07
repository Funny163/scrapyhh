import scrapy
import urllib.parse

from myproject.parsers.product_parser import parse_product_json


START_URLS = [
    'https://alkoteka.com/catalog/slaboalkogolnye-napitki-2',
]

# START_URLS = [
#     'https://alkoteka.com/catalog/slaboalkogolnye-napitki-2',
#     'https://alkoteka.com/catalog/krepkiy-alkogol',
# ]


KRASNODAR_CITY_ID = '4a70f9e0-46ae-11e7-83ff-00155d026416'
ITEMS_ON_PAGE = 100


class AlkotekaSpider(scrapy.Spider):
    name = 'spider_name'

    async def start(self):
        for link in START_URLS:
            category = link.rstrip("/").split("/")[-1]

            category_api_url = (f'https://alkoteka.com/web-api/v1/product?'
                                f'city_uuid={KRASNODAR_CITY_ID}&page=1&per_page={ITEMS_ON_PAGE}&'
                                f'root_category_slug={urllib.parse.quote(category)}')
            yield scrapy.Request(
                url=category_api_url,
                callback=self.parse_category_page,
                cb_kwargs={'category': category}
            )

    def parse_category_page(self, response, category):
        data = response.json()
        total_items = data.get("meta", {}).get("total", 0)
        total_pages = total_items // ITEMS_ON_PAGE + (1 if total_items % ITEMS_ON_PAGE else 0)
        query = urllib.parse.parse_qs(urllib.parse.urlparse(response.url).query)
        current_page = int(query.get("page", [1])[0])

        self.logger.info(f'Обрабатываю страницу {current_page}/{total_pages} (товаров всего: {total_items})')
        for product in data.get('results', []):
            product_slug = product.get('slug', False)
            if product_slug:
                product_url = (f'https://alkoteka.com/web-api/v1/'
                               f'product/{product_slug}?city_uuid={KRASNODAR_CITY_ID}')
                yield scrapy.Request(
                    url=product_url,
                    callback=self.parse_product_page,
                )

        if current_page < total_pages:
            next_page = current_page + 1
            next_url = response.url.replace(f"&page={current_page}", f"&page={next_page}")
            self.logger.info(f'Переход на страницу {next_page}/{total_pages}')

            yield scrapy.Request(
                url=next_url,
                callback=self.parse_category_page,
                cb_kwargs={'category': category}
            )

    @staticmethod
    def parse_product_page(response):
        data = response.json()
        if data.get('success'):
            yield parse_product_json(data=data, url=response.url)
        else:
            print(response.url)
