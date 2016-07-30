# Crawlpy

---

Python web spider/crawler based on [scrapy](http://scrapy.org/) with support for POST/GET login and variable level of recursions/depth.

---


## Requirements

* [python 2.7](https://www.python.org/)
* [lxml](http://lxml.de/)
* [pip](https://pip.pypa.io/en/latest/installing/)

```shell
pip install Scrapy
```

## Usage

```shell

# stdout output
scrapy crawl crawlpy -a config=/path/to/crawlpy.config.json

# save as json (url:, referer:, depth:) to 'urls.json'
scrapy crawl crawlpy -a config=/path/to/crawlpy.config.json -o urls.json -t json

# save as csv (url, referer, depth) to 'urls.csv'
scrapy crawl crawlpy -a config=/path/to/crawlpy.config.json -o urls.csv -t csv
```

## Configuration

Make a copy of [crawlpy.config.json-sample](crawlpy.config.json-sample) (e.g.: `example.com-config.json`) and adjust the values accordingly.

**Note:**
It must be a valid json file (without comments), otherwise `crawlpy` will throw errors parsing json. (Use http://jsonlint.com/ to validate your config file.)

```json
{
    "proto": "http",        // 'http' or 'https'
    "domain": "localhost",  // Only the domain. e.g.: 'example.com' or 'www.example.com'
    "depth": 3,             // Nesting depth to crawl
    "login": {              // Login data
        "enabled": true,    // Do we actually need to do a login?
        "method": "post",   // 'post' or 'get'
        "action": "/login.php", // Where the post or get will be submitted to
        "failure": "Password is incorrect", // The string you will see on login failure
        "fields": {         // Fields to submit to 'action', add more if you need
            "username": "john",
            "password": "doe"
        }
    }
}
```

### Detailed description

|Key|Type|Value|Description|
|---|----|-----|-----------|
|proto|string|`http` or `https`|Is the site you want to crawl running on `http` or `https`?|
|domain|string|Domain or subdomain|The domain or subdomain you want to spider. Nothing outside this domain/subdomain will be touched.|
|depth|integer|0,1,2,3,...|`0`: Crawl indefinetely until every subpage has been reached.<br/>`1`: Only crawl links on the initial page.<br/>`2`: Crawl links on the initial page and everything found on the links of that page.<br/><br/>**Note:** when you do a login, the login page already counts as one level of depth by scrapy itself, but this is rewritten internally to subtract that depth again, so your output will not show that extra depth.|
|login|||Login section|
|enabled|boolean|`true` or `false`|`true`: Do a login prior crawling<br/>`false`: do not login<br/><br/>**Note:**When login is set to `false`, you do not need to fill in the rest of the variables inside the `login` section|
|method|string|`post` or `get`|Method required to execute the login|
|action|string|login page|Relative login page (from the base domain, including leading slash) where the `post` or `get` will go to.|
|failure|string|login failed string|A string that is found on the login page, when the login fails.|
|fields|key-value|`post` or `get` params|POST or GET params required to login.<br/><br/>**Examples:** username, password, hidden-field-name|

## TODO

* Check for dynamic [CSRF](https://en.wikipedia.org/wiki/Cross-site_request_forgery) token prior log in
