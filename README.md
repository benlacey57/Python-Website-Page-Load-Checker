# Performance Monitoring and Reporting

## Python Packages
```sh
pip install selenium python-dotenv plotly streamlit matplotlib requests pandas
```

## Data Storage
Lighthouse: This folder contains the lighthouse reports with a date prefix to retain past JSON reports.

Speed Check: This folder contains a CSV file for every page that was scanned. This includes the timestamp, URL, and time (seconds) taken to render the response.

Logs: This folder contains a sub-folder for each website in the sites config array. There will be one log file for Performance_Scanner.log that can be used for debugging issues. As the system grows, more separated log files may be available.

Reports: This folder will contain custom reports based on a Jinja2 HTML template. It will be used internally and will contain charts and raw data logged to give an overview of the performance and checks done.

Templates: This folder contains the HTML templates that will be used for generating the PDF reports.

## Scripts
### Selenium Installation
Run the install scripts in `scripts/shell/selenium/install-chrome-driver.sh` and `scripts/shell/selenium/install-firefox-driver.sh` to install the browser and selenium drivers needed to control the browser.


## Config Options
This section allows you to specify the websites to run checks on. Authentication is not yet implemented but will be added. You can send a request to the authentication API endpoint to unlock the website and perform the scans.

### Sites Config
```json
 "sites": {    
    "site1": {
        "enabled": true,
        "url": "https://benlacey.co.uk"
    },
    "site2": {
        "enabled": false,
        "url": "https://staging.somedomain.com",
        "authentication": {
            "username": "",
            "password": "testpassword"
        }
    }
},
```

### Pages Config
This configuration allows you to specify the pages you want to audit for performance and load times. You can also specify whether to perform a Google Lighthouse report for specific pages.

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
    }
]
```

## Pending Updates
Performance Scanner Improvements Road Map:

- Allow specifying sites and login credentials for staging.
- Set a sitemap URL; if it can be accessed, parse the URLs and scan all pages for load times.
- Push the CSV data to Google Sheets (separate worksheet for each page).
- Run a lighthouse scan on select key pages (the current "pages" list).
- Generate a report of the speeds as a Jinja2 template with HTML.
- Produce charts on the CSV data to show speeds over time.

### Request Options
Specify options for the requests module (not yet implemented).

```json
"request_options": {
    "retries": 3
}
```

### Headers
Specify the user agents and select one for each script invocation (not yet implemented).

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