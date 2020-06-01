hrefs = ['https://www.sxglpx.com/contact/#payment', 'https://www.sxglpx.com/about/banquansc/',
         'https://www.sxglpx.com/about/', 'https://www.sxglpx.com/news/', 'https://www.sxglpx.com/about/hr/',
         'https://www.sxglpx.com/', 'https://www.sxglpx.com/', 'https://www.sxglpx.com/baiduseo/',
         'https://www.sxglpx.com/googleseo/', 'https://www.sxglpx.com/waimaozhan/', 'https://www.sxglpx.com/case/',
         'https://www.sxglpx.com/case/googlecase/', 'https://www.sxglpx.com/case/webcase/',
         'https://www.sxglpx.com/userlearning/', 'https://www.sxglpx.com/seoresearch/',
         'https://www.sxglpx.com/wzjsjy/', 'https://www.sxglpx.com/wmtgjy/', 'https://www.sxglpx.com/contact/', '?s=',
         '#', 'https://www.sxglpx.com', 'https://www.sxglpx.com/waimaozhan/', 'https://www.sxglpx.com/wmjyfx/facebook/',
         'https://www.sxglpx.com/contact/', 'tel:18537972228', 'tel:18538866292',
         'https://www.sxglpx.com/study/seojqwzmwbrhtj/', 'https://www.sxglpx.com/study/wzbjcwckdzyx/',
         'https://www.sxglpx.com/study/wznrzlyysyjpssmys/', 'https://www.sxglpx.com/study/wzwzxgdseoyx/',
         'http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=41030502000148', '#top']

from kspider.urls import norm_url

for href in hrefs:
    print(
        norm_url(url=href,index='https://www.sxglpx.com/',rel='https://www.sxglpx.com/123123123123')
    )
