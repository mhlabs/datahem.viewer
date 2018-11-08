# BigQuery Python builder

## Introduction
This builder supports the BigQuery Python API.

## Usage
From this folder run:

```
gcloud builds submit --config=cloudbuild.yaml .
```

## Python notes

Python has several different dependency management tools, which interact in
different ways with containers.  In this case we use `virtualenv` to setup an
isolated folder inside the container with the libraries we need.  As a result of
this, be sure that your first build step loads the `virtualenv` environment.
See examples for details.

Additional libraries can be added by creating another container based on this
one, for example:

```
FROM gcr.io/my-project/bigquery-python

RUN /bin/bash -c "source venv/bin/activate"

RUN pip install my-library
...
```

This container uses Python 2.