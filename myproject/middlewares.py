import os
import random


USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36',
]


class ProxyMiddleware:
    def __init__(self, proxy_file, spider=None):
        self.proxy_list = []
        self.logged = False
        proxy_path = os.path.join(os.path.dirname(__file__), '..', proxy_file)
        proxy_path = os.path.abspath(proxy_path)

        if os.path.exists(proxy_path):
            with open(proxy_path) as f:
                self.proxy_list = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        if spider:
            if self.proxy_list:
                spider.logger.info(f'Найдено {len(self.proxy_list)} прокси.')
            else:
                spider.logger.info('Файл proxy.txt не найден или пуст, работаем без прокси')

    @classmethod
    def from_crawler(cls, crawler):
        proxy_file = crawler.settings.get('PROXY_LIST_FILE', 'proxy.txt')
        return cls(proxy_file, spider=crawler.spider)

    def process_request(self, request, spider):
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = proxy


class RandomUserAgentMiddleware:
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(USER_AGENTS)

    def process_request(self, request, spider):
        ua = random.choice(self.user_agents)
        request.headers['User-Agent'] = ua
