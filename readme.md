# GitHub PullRequest Loader

## Initializing

To initialize dependencies run `pip install requirements.txt`

To start postgres instance run `docker-compose up`

## Running

To load data into db run `python app/loader.py <api-key> <repo-name>`, where api-key - github api key, repo-name e.g. `apache/spark` (`apache/couchdb-documentation` for small test - 511 prs).
This will drop data and re-load into database.

To show sample statistics run `python app/report.py`

To run unit-tests run ` python app/test.py`

`app/models.py` contains model definitions.

## Limitations

Given the requirements of the assignment, for every PR the list of files has to be loaded which results in doing separate api calls for every PR which results in low performance. There is no api to batch get all prs + files (as per what I see in docs). Executing sequentially results in ~50min to load ~5000 prs. Hence the performance improvement - to execute list-files requests in parallel using thread pool. Github limit for items per page is 100. With the given enhancement loading of 5000 prs should go in ~10minutes although limit of 5000 api calls will be reached sooner than that.
In any case partial results are loaded into db per page.

