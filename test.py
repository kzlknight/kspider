from kspider.spider import Spider
from kspider.http import Response,Request
import time

class MySpider(Spider):
    index = 'https://www.sxglpx.com/'

    def start_request(self):
        yield Request(
            url = 'https://www.sxglpx.com/googleseo/',
            callback=self.parse1,
            dont_filter=True,
        )

    def parse1(self,response):
        print(response.xpath_all('//h2'))

if __name__ == '__main__':

    from kspider.processer import Processer
    p = Processer(spider=MySpider())
    p.run()
    time.sleep(5)

    p.close()