# datahem.viewer

Generate datasets and views in BigQuery and set up access accordingly. Run it with cloud build (CI/CD) and trigger by push to github repo where view definitions are kept. 

## Usage
1. Clone this repo and push to your own private repo (or fork this repo if you are ok with your repo being public). Some good instructions here: https://stackoverflow.com/questions/10065526/github-how-to-make-a-fork-of-public-repository-private
2. Register the bigquery-python container (se readme.md in bigquery-python folder) and then set up a trigger in google cloud build and authenticate cloud build to access your github repo.
3. Define your views in json files under the views folder. You can create your own folders under the views folder.
4. Create one file per view definition. The name of the json-file becomes the name of the view, i.e. view_store_orderstatus.json will be view_store_orderstatus in bigquery.
5. Two datasets will be generated for each group, one with READER access (_ro suffix) and one with WRITER access (_rw suffix). The name of the dataset will be the local-part of the group email address plus named suffix , ie 'developers@ datahem.org' -> 'developers_ro' and 'developers_rw' and access will only be given to members of the developers email group.

Example view definition
```json
{
    "groups":["developers@datahem.org", "analysts@datahem.org"],
    "sql":"SELECT * FROM `{project}.shared_views.test_view`"
}
```

## Version
## 0.7.0 (2018-11-07): Cloud Build with custom builder
Changed the collector to use cloud endpoints for better security, monitoring, logging and RESTful URLs