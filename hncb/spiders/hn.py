import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from hncb.items import Article


class HnSpider(scrapy.Spider):
    name = 'hn'
    start_urls = ['https://www.hncb.com.tw/wps/portal/HNCB/morenews']

    def parse(self, response):
        links = response.xpath('//div[@class="box-panel-content"]//a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@title="Link to next page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'connect' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2[@class="content-title"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="news-date text-right mb10"]//text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="col-md-10 col-md-offset-1"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
