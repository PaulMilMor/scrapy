import scrapy

# Titulo = //h1/a/text()
# Citas = //span[@class="text" and @itemprop="text"]/text()
# Top ten tags = //div[contains(@class, "tags-box")]/span[@class="tag-item"]/a/text()
# Next page button = //ul[@class="pager"]/li[@class="next"]/a/@href


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'https://quotes.toscrape.com/'
    ]

    # Esto está deprecado
    # custom_settings = {
    #     'FEED_URI': 'quotes.json',
    #     'FEED_FORMAT': 'json'
    # }

    custom_settings = {
        'FEEDS': {
            'quotes.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'fields': None,
                'indent': 4,
                'item_export_kwargs': {
                    'export_empty_fields': True
                }
            }
        },
        'CONCURRENT_REQUESTS': 24,
        'MEMUSAGE_LIMIT_MB': 2048,
        'MEMUSAGE_NOTIFY_MAIL': [''],
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'PepitoMartinez'
    }

    def parse_only_quotes(self, response, **kwargs):
        if kwargs:
            quotes = kwargs['quotes']
        quotes.extend(response.xpath(
            '//span[@class="text" and @itemprop="text"]/text()').getall())

        next_page_button_link = response.xpath(
            '//ul[@class="pager"]/li[@class="next"]/a/@href').get()

        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes': quotes})
        else:
            yield {
                'quotes': quotes
            }

    def parse(self, response):

        title = response.xpath('//h1/a/text()').get()

        quotes = response.xpath(
            '//span[@class="text" and @itemprop="text"]/text()').getall()

        top_tags = response.xpath(
            '//div[contains(@class, "tags-box")]/span[@class="tag-item"]/a/text()').getall()

        top = getattr(self, 'top', None)
        if top:
            top = int(top)
            top_tags = top_tags[:top]

        yield {
            'title': title,
            'top_tags': top_tags
        }

        next_page_button_link = response.xpath(
            '//ul[@class="pager"]/li[@class="next"]/a/@href').get()

        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes': quotes})
