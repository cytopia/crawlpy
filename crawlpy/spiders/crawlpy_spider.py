# -*- coding: utf-8 -*-

"""Module Doc
Based on:
https://stackoverflow.com/questions/5851213/crawling-with-an-authenticated-session-in-scrapy
http://thuongnh.com/building-a-web-crawler-with-scrapy/
"""
import os       # file path checks
import re       # regex
import logging  # logger
import json     # json extract
#import scrapy   # scrapy framework

from scrapy.http                import Request, FormRequest
from scrapy.linkextractors      import LinkExtractor
from scrapy.selector            import Selector
from scrapy.spiders             import Rule
from scrapy.spiders.init        import InitSpider

from crawlpy.items import CrawlpyItem


################################################################################
# Spider Class
################################################################################
class CrawlpySpider(InitSpider):
    """
    Crawlpy Class
    """
    # pylint: disable=too-many-instance-attributes

    ########################################
    # Scrapy Variables
    ########################################
    name = "crawlpy"


    ########################################
    # Variables to be initialized by config
    ########################################

    # Main JSON Configuration dict
    config = {}


    # Link extraction rules
    rules = ()


    # scrapy required vars
    allowed_domains = []
    start_urls = []



    ########################################
    # Non scrapy variables
    ########################################

    depth = 0           # Limit depth (0: no limit)
    base_url = ''       # (http|https)://domain.tld

    # Login data
    login_required = False
    login_page = ''
    login_method = ''   # 'post' or 'get'
    login_data = {}     # Post data
    login_failure = ''  # Error string on unsuccessful login


    # Abort flag
    abort = False



    ########################################
    # Methods
    ########################################

    #----------------------------------------------------------------------
    def __init__(self, *a, **kw):
        """Constructor: overwrite parent __init__ function"""

        # Call parent init
        super(CrawlpySpider, self).__init__(*a, **kw)

        # Get command line arg provided configuration param
        config_file = kw.get('config')

        # Validate configuration file parameter
        if not config_file:
            logging.error('Missing argument "-a config"')
            logging.error('Usage: scrapy crawl crawlpy -a config=/path/to/config.json')
            self.abort = True

        # Check if it is actually a file
        elif not os.path.isfile(config_file):
            logging.error('Specified config file does not exist')
            logging.error('Not found in: "' + config_file + '"')
            self.abort = True

        # All good, read config
        else:
            # Load json config
            fpointer = open(config_file)
            data = fpointer.read()
            fpointer.close()

            # Store config in dict
            self.config = json.loads(data)

            # Set scrapy globals
            self.allowed_domains = [self.config.get('domain')]
            self.start_urls = [self.config.get('proto') + '://' + self.config.get('domain') + '/']
            self.rules = (
                Rule(
                    LinkExtractor(
                        allow_domains=(self.allowed_domains),
                        unique=True,
                        deny=('logout'),
                    ),
                    callback='parse',
                    follow=True
                ),
            )

            # Set misc globals
            self.depth = self.config.get('depth')
            self.base_url = self.config.get('proto') + '://' + self.config.get('domain')
            self.login_required = self.config.get('login').get('enabled')


            if self.login_required:
                self.login_page = self.config.get('proto') + '://' + self.config.get('domain') + \
                                  self.config.get('login').get('action')
                self.login_method = str(self.config.get('login').get('method'))
                self.login_failure = str(self.config.get('login').get('failure'))
                self.login_data = self.config.get('login').get('fields')



    #----------------------------------------------------------------------
    def init_request(self):
        """This function is called before crawling starts."""

        # Do not start a request on error,
        # simply return nothing and quit scrapy
        if self.abort:
            return

        # Do a login
        if self.login_required:
            # Start with login first
            return Request(url=self.login_page, callback=self.login)
        else:
            # Start with pase function
            return Request(url=self.base_url, callback=self.parse)


    #----------------------------------------------------------------------
    def login(self, response):
        """Generate a login request."""

        self.log('Login called')
        return FormRequest.from_response(
            response,
            formdata=self.login_data,
            method=self.login_method,
            callback=self.check_login_response
        )


    #----------------------------------------------------------------------
    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in.
        """
        if self.login_failure not in response.body:
            # Now the crawling can begin..
            self.log('Login successful')
            return self.initialized()
        else:
            # Something went wrong, we couldn't log in, so nothing happens.
            logging.error('Unable to login')


    #----------------------------------------------------------------------
    def parse(self, response):
        """
        Scrapy parse callback
        """

        # Get current nesting level
        curr_depth = response.meta.get('depth', 1)
        if self.login_required:
            curr_depth = curr_depth - 1 # Do not count the login page as nesting depth

        # Yield current url
        item = CrawlpyItem()  # could also just be `item = dict()`
        item['url'] = response.url
        item['depth'] = curr_depth
        item['referrer'] = response.meta.get('referrer', '')
        yield item

        # Dive deeper?
        if curr_depth < self.depth or self.depth == 0:
            links = LinkExtractor().extract_links(response)
            for link in links:
                yield Request(link.url, meta={'depth': curr_depth+1, 'referrer': response.url})


