# -*- coding: utf-8 -*-

"""Module Doc"""
import sys      # Encoding
import os       # file path checks
import logging  # logger
import json     # json extract

from scrapy.http                import Request, FormRequest
from scrapy.linkextractors      import LinkExtractor
from scrapy.spiders             import Rule
from scrapy.spiders.init        import InitSpider

from crawlpy.items import CrawlpyItem

# Fix UTF-8 problems inside dict()
reload(sys)
sys.setdefaultencoding('utf8')


################################################################################
# Spider Class
################################################################################
class CrawlpySpider(InitSpider):
    """
    Crawlpy Class
    """

    ########################################
    # Scrapy Variables
    ########################################
    name = "crawlpy"

    # Link extraction rules
    # To be initialized
    rules = ()


    # scrapy domain/url vars
    # To be initialized
    allowed_domains = []
    start_urls = []


    ########################################
    # Configuration
    ########################################

    # Main JSON Configuration dict
    config = None
    config_defaults = dict({
        'proto': 'http',
        'domain': 'localhost',
        'depth': 3,
        'login': {
            'enabled': False,
            'method': 'post',
            'action': '/login.php',
            'failure': 'Password is incorrect',
            'fields': {
                'username': 'john',
                'password': 'doe'
            }
        }
    })


    ########################################
    # Helper variables
    ########################################

    base_url = ''       # (http|https)://domain.tld
    login_url = ''      # (http|https)://domain.tld/path/to/login

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

            # convert JSON to dict
            config = json.loads(data)

            # fill in default values for missing values
            self.config = dict()
            self.config['proto'] = str(config.get('proto', self.config_defaults['proto']))
            self.config['domain'] = str(config.get('domain', self.config_defaults['domain']))
            self.config['depth'] = int(config.get('depth', self.config_defaults['depth']))
            self.config['login'] = dict()
            self.config['login']['enabled'] = bool(config.get('login', dict()).get('enabled', self.config_defaults['login']['enabled']))
            self.config['login']['method'] = str(config.get('login', dict()).get('method', self.config_defaults['login']['method']))
            self.config['login']['action'] = str(config.get('login', dict()).get('action', self.config_defaults['login']['enabled']))
            self.config['login']['failure'] = str(config.get('login', dict()).get('failure', self.config_defaults['login']['failure']))
            self.config['login']['fields'] = config.get('login', dict()).get('fields', self.config_defaults['login']['fields'])

            # Set scrapy globals
            self.allowed_domains = [self.config['domain']]
            self.start_urls = [self.config['proto'] + '://' + self.config['domain'] + '/']
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
            self.base_url = self.config['proto'] + '://' + self.config['domain']
            self.login_url = self.config['proto'] + '://' + self.config['domain'] + \
                                  self.config['login']['action']



    #----------------------------------------------------------------------
    def init_request(self):
        """This function is called before crawling starts."""

        # Do not start a request on error,
        # simply return nothing and quit scrapy
        if self.abort:
            return

        logging.info('All set, start crawling with depth: ' + str(self.config['depth']))

        # Do a login
        if self.config['login']['enabled']:
            # Start with login first
            logging.info('Login required')
            return Request(url=self.login_url, callback=self.login)
        else:
            # Start with pase function
            logging.info('Not ogin required')
            return Request(url=self.base_url, callback=self.parse)


    #----------------------------------------------------------------------
    def login(self, response):
        """Generate a login request."""

        return FormRequest.from_response(
            response,
            formdata=self.config['login']['fields'],
            method=self.config['login']['method'],
            callback=self.check_login_response
        )


    #----------------------------------------------------------------------
    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in.
        """
        if self.config['login']['failure'] not in response.body:
            # Now the crawling can begin..
            logging.info('Login successful')
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
        if self.config['login']['enabled']:
            curr_depth = curr_depth - 1 # Do not count the login page as nesting depth

        # Yield current url item
        item = CrawlpyItem()
        item['url'] = response.url
        item['depth'] = curr_depth
        item['referer'] = response.meta.get('referer', '')
        yield item

        # Dive deeper?
        if curr_depth < self.config['depth'] or self.config['depth'] == 0:
            links = LinkExtractor().extract_links(response)
            for link in links:
                yield Request(link.url, meta={'depth': curr_depth+1, 'referer': response.url})
