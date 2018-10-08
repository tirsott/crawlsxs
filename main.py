from scrapy import cmdline
# cmdline.execute('scrapy crawl text'.split())

import os
os.chdir('job/spiders')
cmdline.execute('scrapy runspider job51.py'.split())
# cmdline.execute('scrapy runspider crawljob.py'.split())