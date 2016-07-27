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

    rules = (
        Rule(
            LinkExtractor(
                allow=("", ),
                deny=('logout'),
            ),
            callback='parse',
            follow=True
        ),
    )

    ########################################
    # Variables to be initialized by config
    ########################################

    # Main JSON Configuration dict
    config = {}

    # scrapy required vars
    allowed_domains = []
    start_urls = []


    # Crawling depth
    depth = 0

    # Login data
    login_required = False
    login_page = ''
    login_method = ''   # 'post' or 'get'
    login_data = {}     # Post data
    login_failure = ''  # Error string on unsuccessful login

    base_url = ''       # (http|https)://domain.tld


    ########################################
    # Non scrapy variables
    ########################################

    # Abort flag
    abort = False

    # Keep track about non-unique links
    uniques = []


    ########################################
    # Methods
    ########################################

    #----------------------------------------------------------------------
    def __init__(self, *a, **kw):
        """Overwrite __init__ function"""

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

        # Read json configuration file into python dict
        fpointer = open(config_file)
        data = fpointer.read()
        fpointer.close()
        self.config = json.loads(data)

        # Set scrapy globals
        self.allowed_domains = [self.config.get('domain')]
        self.start_urls = [self.config.get('proto') + '://' + self.config.get('domain') + '/']

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


        # Call parent init
        super(CrawlpySpider, self).__init__(*a, **kw)





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
        if response.meta.has_key('depth'):
            curr_depth = response.meta['depth']
        else:
            curr_depth = 1


        # Only crawl the current page if we hit a HTTP-200
        if response.status == 200:
            hxs = Selector(response)
            links = hxs.xpath("//a/@href").extract()

            # We stored already crawled links in this list
            crawled_links = []

            # Pattern to check proper link
            linkPattern  = re.compile("^(?:http|https):\/\/(?:[\w\.\-\+]+:{0,1}[\w\.\-\+]*@)?(?:[a-z0-9\-\.]+)(?::[0-9]+)?(?:\/|\/(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+)|\?(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+))?$")

            for link in links:

                # Link could be a relative url from response.url
                # such as link: '../test', respo.url: http://dom.tld/foo/bar
                if link.find('../') == 0:
                    link = response.url + '/' + link
                # Prepend BASE URL if it does not have it
                elif 'http://' not in link and 'https://' not in link:
                    link = self.base_url + link


                # If it is a proper link and is not checked yet, yield it to the Spider
                if (link
                        and linkPattern.match(link)
                        and link.find(self.base_url) == 0):
                        #and link not in crawled_links
                        #and link not in uniques):

                    # Check if this url already exists
                    re_exists = re.compile('^' + link + '$')
                    exists = False
                    for i in self.uniques:
                        if re_exists.match(i):
                            exists = True
                            break

                    if not exists:
                        # Store the shit
                        crawled_links.append(link)
                        self.uniques.append(link)

                        # Do we recurse?
                        if curr_depth < self.depth:
                            request = Request(link, self.parse)
                            # Add meta-data about the current recursion depth
                            request.meta['depth'] = curr_depth + 1
                            yield request
                        else:
                            # Nesting level too deep
                            pass
                else:
                    # Link not in condition
                    pass


            #
            # Final return (yield) to user
            #
            for url in crawled_links:
                #print "FINAL FINAL FINAL URL: " + response.url
                item = CrawlpyItem()
                item['url'] = url
                item['depth'] = curr_depth

                yield item
            #print "FINAL FINAL FINAL URL: " + response.url
            #item = CrawlpyItem()
            #item['url'] = response.url
            #yield item
        else:
            # NOT HTTP 200
            pass
