# Performance Monitoring and Reporting


## Python Packages
pip install selenium python-dotenv plotly streamlit matplotlib requests pandas

## Selenium
Run install script in `scripts/shell/selenium/install-chrome-driver.sh` and `scripts/shell/selenium/install-firefox-driver.sh` to install the browser and selenium driver to control the browser.

## Config
### Sites
This is where you can specify the websites to run checks on. The authentication is not yet implemented but it needs to be. We can send a request to the authentication API end point in order to unlock the website and perform the scans.

### Pages
This configuration allows us to specify what pages we want to audit for performance and load times. You can specify what pages you want to perform a Google Lighthouse report for so you have control over this. I expect I will add in more flags to the config for other per-page scans.

```json
"pages": [
    {
        "url": "/",
        "name": "home",
        "lighthouse_scan": false
    },
    {
        "url": "/about/",
        "name": "about",
        "lighthouse_scan": false
    },
    {
        "url": "/contact/",
        "name": "contact",
        "lighthouse_scan": false
    },
]
```

---

## Pending Updates
Performance Scanner Improvements Road Map:

- Allow us to specify sites and login credentials for staging
- Set a sitemap URL, if it can be accessed parse the URLs and do a scan of all pages for load times
- Push the CSV data to Google Sheets (separate worksheet for each page?)
- Set it up to run a lighthouse scan on select key pages (the current "pages" list)
- Generate a report of the speeds as a Jinja2 template with html
- Produce Charts on the CSV data to show speeds over time

### Request Options
This is where we can specify options for the requests module, this is not yet implemented but would be good to consider.

```json
"request_options": {
    "retries": 3
}
```

### Headers
This has not yet been implemented but being able to specify the user agents and select one for each script invokation.

```json
"headers": {
    "desktop-user-agents": {
        "chrome": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
        ],
        "firefox": [],
        "safari": [],
        "edge": []
    },
    "mobile-user-agents": {
        "chrome": [],
        "firefox": [],
        "safari": [],
        "edge": []
    }
}
```

## Data
### Lighthouse
This folder contains the lighthouse reports with a date prefix to retain past JSON reports.

### Speed Check
This folder contains a CSV file for every page that was scanned. This includes the timestamp, URL and time (seconds) took to render the response.


## Logs
This folder contains a sub-folder for each website in the sites config array. There will be one log file for Performance_Scanner.log that can be used for debugging issues. It's quite verbose and self explainatory. As the system grows there may be more separated log files available.


## Reports
This folder will contain custom reports based on a Jinja2 HTML template. This will be used internally and will contain charts and raw data that was logged to give an overview of the performance and checks done.

## Templates
This folder contains the HTML templates that will be used for generating the PDF reports.