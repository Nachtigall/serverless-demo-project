# Serverless demo project

## Hey there!

In this repo, you can find my approach solving tech task. 

### General thoughts:

The biggest issue was not with the serverless logic, but rather with Twitter itself. Since the usage of third party libs was forbidden - I had to scrape Twitter by myself. Turned out, that page has a bunch of javascript, which is not possible to scrape via standard python libs like requests or so. My approach was to use `selenium` and chrome browser to wait until the page is fully loaded. Here, I got into another issue - AWS Lambda allows only headless browsers, however, Twitter doesn't like that, since it's not a supported browser.

So, taking into account all of this my solution is to use selenium with a headless browser, which in a hacky way pretends to be a "normal" browser.

The next phase was to deploy everything to AWS - and here run into an issue with lambda layers. For some reason, couldn't make the lambda function work with selenium/chrome layers. So, ended up creating a docker image, which contains the code itself + selenium and chrome binaries (it's slower to operate, but it's a working solution).

#### Endpoints:
- `https://l05dabcqeb.execute-api.us-east-1.amazonaws.com/scrape`
Body - `{"handle": "elonmusk"}`

An endpoint will scrape data from Twitter by the requested handle and store it at AWS S3. The response contains presigned URL which can be used to download the image.

- `https://l05dabcqeb.execute-api.us-east-1.amazonaws.com/users/{handle}/profile_pic`

An endpoint will return information about the exact handle. Empty response if data is not present

- `https://l05dabcqeb.execute-api.us-east-1.amazonaws.com/users`

A paginated endpoint will return information about all handles (3 items in one response) and additional `next_token` data. This `next_token` parameter can be used in calling endpoint with pagination like `/users?next_token={next_token}`


#### Python dependencies:
Moved project requirements in `Pipfile` via `pipenv`. With old-style `requirements.txt` it's quite hard to manage all dependencies. Better solutions for that to have something like `Pipenv`, `Poetry`, etc.

To spin up local env - just run `pipenv shell` instead of installing all libs locally.

#### Local development:
- `sls s3 start --stage local`
- `sls dynamodb start --stage local`
- `sls wsgi serve -p 8001 --stage local`

#### Dev experience:
Added `black` and `isort` libraries to keep sorting and code always in the same style. Also, as an option could be to add `mypy` to enforce type hints.

#### Storage system:
As a storage system was used `DynamoDB` (`handle: s3_url` as `key: value` storage)+ `S3 bucket` (as image storage). There are no relations between handles, so, there is no reason to choose something more complex like RDS or so.

#### Future enhancements:
- speed up selenium logic. Maybe there is a way to omit this framework - need to research
- tests (working on this ATM)
- user authorization (with user authorization we can build a system to serve only own data)
- logging system
- ENVs proper management (now it's just simply structured with no smart logic at all)
- etc
