import time


def get_variants(description_blocks: list) -> int:
    for block in description_blocks:
        if block['code'] == 'obem':
            if block.get('min') and block.get('max') and block['min'] != block['max']:
                return 2
            if block.get('min'):
                return 1
    return 1


def get_stock(data: dict) -> dict:
    return {
        'in_stock': data.get('available', False),
        'count': data.get('quantity_total', 0) or 0
    }


def get_product_title(name: str, description_blocks: list) -> str:
    """
    Формирует заголовок/название товара.

    Если в карточке товара указан цвет или объем, но они отсутствуют в названии,
    функция добавляет их в title в формате: "{Название}, {Цвет}, {Объем}".
    :param name: Название товара из карточки
    :param description_blocks: Список блоков описания товара
    :return: Строка с полным заголовком товара, включая цвет и объем,
             если они присутствуют и отсутствуют в исходном названии.
    """
    answer = name
    color = None
    volume = None
    for block in description_blocks:
        if block['code'] == 'cvet':
            values = block.get('values') or []
            if values:
                color = values[0].get('name')
        if block['code'] == 'obem':
            if block.get('max'):
                volume = f"{block['min']}{block.get('unit', '')}"
    if color and color not in answer:
        answer = f'{answer}, {color}'
    if volume and volume not in answer:
        answer = f'{answer}, {volume}'
    return answer


def get_price_blocks(data: dict) -> dict:
    price = data.get('price')
    prev_price = data.get('prev_price', 0)
    discont = None

    answer = {
        'current': float(price),
        'original': float(prev_price) if prev_price and prev_price > price else float(price),
    }
    if prev_price:
        discont = str(100 - round(price / prev_price * 100)) + '%'

    answer['sale_tag'] = discont
    return answer


def get_assets(data: dict) -> dict:
    return {
        'main_image': data.get('image_url'),
        'set_images': [data.get('image_url')] if data.get('image_url') else [],
        'view360': [],
        'video': []
    }


def get_product_metadata(data: dict) -> dict:
    metadata = {}
    description = ''
    for block in data.get('text_blocks', []):
        if block['title'] == 'Описание':
            description = block.get('content', '')
        else:
            metadata[block['title']] = block.get('content', '')
    metadata['__description'] = (description.strip().replace('\n', '. ').
                                 replace('<br>', '').replace('..', '.'))

    for block in data.get('description_blocks', []):
        values = block.get('values') or []
        if values:
            metadata[block['title']] = ', '.join(
                f"{v.get('name')} {block.get('unit', '')}" for v in values if v.get('name'))
        elif block.get('min') is not None and block.get('max') is not None:
            metadata[block['title']] = f"{block['min']}{block['unit']}"

    metadata['Артикул'] = str(data.get('vendor_code'))
    metadata['Код товара'] = data.get('uuid')
    metadata['Страна'] = data.get('country_name')

    gastronomics = data.get('gastronomics', {})
    gastronomy_titles = []
    if isinstance(gastronomics, dict):
        for group in gastronomics.values():
            for item in group:
                title = item.get('title')
                if title:
                    gastronomy_titles.append(title)

    # Довольно сложно читаемый list comprehension в данном случае
    # gastronomy_titles = [
    #     item["title"]
    #     for group in data.get('gastronomics', {}).values()
    #     for item in group
    #     if item.get('title')
    # ]

    metadata['Гастрономические сочетания'] = gastronomy_titles
    return metadata


def parse_product_json(data: dict, url: str) -> dict:
    """
    Обработка JSON продукта и возвращения словаря с необходимыми данными

    :param data: JSON (словарь) с данными о товаре
    :param url: ссылка на товар
    :return: dict с распарсенными полями
    """

    answer = dict()
    data: dict = data['results']
    answer['timestamp'] = int(time.time())
    answer['RPC'] = str(data['uuid'])
    answer['url'] = url
    answer['title'] = get_product_title(data['name'], data.get('description_blocks', []))
    answer['marketing_tags'] = [i['title'] for i in data.get('filter_labels', []) if i.get('title')]
    answer['brand'] = next(
        (k['name'] for block in data.get('description_blocks', [])
         if block['code'] == 'brend' for k in block.get('values', [])),
        ''
    ),

    answer['section'] = [data['category']['parent']['name'], data['category']['name']]  # Иерархия разделов, например:
    answer['price_data'] = get_price_blocks(data)
    answer['stock'] = get_stock(data)
    answer['assets'] = get_assets(data)

    answer['variants'] = get_variants(data.get('description_blocks', []))
    answer['metadata'] = get_product_metadata(data)

    return answer
