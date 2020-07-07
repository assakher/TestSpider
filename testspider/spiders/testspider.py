import scrapy
import re


class GoogleSpider(scrapy.Spider):
    name = 'test'

    start_urls = [u"https://www.google.com/search?q=%D0%94%D0%BE%D1%81%D1%82%D0%BE%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%87%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D0%B8+%D0%A1%D0%B0%D0%BD%D0%BA%D1%82+%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3"]

    def parse(self, response):
        # gets links of all search results on page 1 of google
        searchresults = [re.search(r"q=([^;]*)&sa", i).group(1)
                         for i in response.css('div.kCrYT a::attr(href)').getall()
                         if i is not None]
        print(searchresults)
        # Running custom parser for 3 chosen sites
        yield scrapy.Request(searchresults[6], callback=self.parse_spbguide)
        yield scrapy.Request(searchresults[8], callback=self.parse_tripzaza)
        yield scrapy.Request(searchresults[9], callback=self.parse_allmyworld)

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
        imgs = response.css('img,alignignore::attr(src)').getall()
        for i in range(len(titles)):
            yield {
                'title': titles[i],
                'descr': response.xpath(f'//*[@id="post-35370"]/div[1]/h2[{i}]/following-sibling::p[1]/text()').get(),
                'img': imgs[i]
            }
