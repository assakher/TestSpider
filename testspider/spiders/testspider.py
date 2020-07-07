import scrapy
import re
from .cfg import SEARCH_ENGINE, QUERY


class GoogleSpider(scrapy.Spider):
    name = 'test'

    start_urls = [SEARCH_ENGINE + QUERY]

    def parse(self, response):
        # gets links of all search results on page 1 of google
        searchresults = [re.search(r"q=([^;]*)&sa", i).group(1)
                         for i in response.css('div.kCrYT a::attr(href)').getall()
                         if i is not None]
        supported_sites = {
            'https://www.spb-guide.ru/': self.parse_spbguide,
            'https://www.tripzaza.com/ru/destinations/luchshie-dostoprimechatelnosti-sankt-peterburga/': self.parse_tripzaza,
            'https://allmyworld.ru/dostoprimechatelnosti-sankt-peterburga/': self.parse_allmyworld
        }

        for result in searchresults:
            if result in supported_sites:
                yield scrapy.Request(result, callback=supported_sites[result])

    def parse_spbguide(self, response):
        for item in response.css('div.index23')[:-2]:
            yield {
                'title': item.css('h2::text').get(),
                'descr': item.css('p.dim1::text')[0].get() + item.css('p,dim1::text')[1].get(),
                'img': r'https://www.spb-guide.ru/' + item.css('img::attr(src)').get()
            }

    def parse_tripzaza(self, response):
        content_div = "div.single-post-content.clearfixr"
        titles = response.css(f'{content_div} h3::text').getall()
        descrs = response.css(f'{content_div} p::text')[2::].getall()
        imgs = response.css(f'{content_div} img::attr(src)').getall()
        for i in range(len(titles)):
            yield {
                'title': titles[i],
                'descr': descrs[i],
                'img': imgs[i]
            }

    def parse_allmyworld(self, response):
        titles = response.css('h2::text').getall()
        imgs = response.css('p img::attr(src)').getall()
        for i in range(len(titles)):
            yield {
                'title': titles[i],
                'descr': response.xpath(f'//*[@id="post-35370"]/div[1]/h2[{i}]/following-sibling::p[1]/text()').get(),
                'img': imgs[i]
            }
