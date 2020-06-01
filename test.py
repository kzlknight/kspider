from kspider.spider import Spider
from kspider.http import Response,Request
from kspider.urls import norm_url
import time

class MySpider(Spider):
    index = 'https://www.sxglpx.com/'

    def start_request(self):
        yield Request(
            url = '/about',
            callback=self.parse1,
            dont_filter=True,
        )

    def parse1(self,response):
        print(response.request.url)
        print(response.body)
        for href in response.xpath_all('//a/@href'):
            print('【%s】' % href)
            yield response.follow(
                url = href,
                callback = self.parse2,
                dont_filter=True,
            )

    def parse2(self,reponse):
        print('ok')




if __name__ == '__main__':

    from kspider.processer import Processer
    p = Processer(spider=MySpider())
    p.run()
    # request = Request(url='/top')
    # request.url = norm_url(url=request.url, index='https://www.sxglpx.com/', rel='https://www.sxglpx.com/contact')
    # print(request.url)
    # print(request.to_str())