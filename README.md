# Crawlpy

---

Python web spider/crawler based on [scrapy](http://scrapy.org/) with support for POST/GET login and variable level of recursions/depth.

---


## Requirements

```shell
pip install Scrapy
```

## Usage

```shell

# stdout output
scrapy crawl crawlpy -a config=/path/to/crawlpy.config.json

# save to json (url:, depth:)
scrapy crawl crawlpy -a config=~/repo/crawlpy/crawlpy.config.json -o urls.json -t json

# save to csv (url, depth)
scrapy crawl crawlpy -a config=~/repo/crawlpy/crawlpy.config.json -o urls.csv -t csv
```

## Configuration

Make a copy of [crawlpy.config.json-sample](crawlpy.config.json-sample) (e.g.: `example.com-config.json`) and adjust the values accordingly.

**Note:**
It must be a valid json file (without comments), otherwise `crawlpy` with throw errors parsing json.

```json

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
```

