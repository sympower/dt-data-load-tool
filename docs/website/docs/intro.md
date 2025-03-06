---
title: Introduction
description: Introduction to data_load_tool
keywords: [introduction, who, what, how]
---

import snippets from '!!raw-loader!./intro-snippets.py';

# Getting started

![data_load_tool pacman](/img/dlt-pacman.gif)

## What is data_load_tool?

data_load_tool is an open-source Python library that loads data from various, often messy data sources into well-structured, live datasets. It offers a lightweight interface for extracting data from [REST APIs](./tutorial/rest-api), [SQL databases](./tutorial/sql-database), [cloud storage](./tutorial/filesystem), [Python data structures](./tutorial/load-data-from-an-api), and [many more](./dlt-ecosystem/verified-sources).

data_load_tool is designed to be easy to use, flexible, and scalable:

- data_load_tool infers [schemas](./general-usage/schema) and [data types](./general-usage/schema/#data-types), [normalizes the data](./general-usage/schema/#data-normalizer), and handles nested data structures.
- data_load_tool supports a variety of [popular destinations](./dlt-ecosystem/destinations/) and has an interface to add [custom destinations](./dlt-ecosystem/destinations/destination) to create reverse ETL pipelines.
- data_load_tool can be deployed anywhere Python runs, be it on [Airflow](./walkthroughs/deploy-a-pipeline/deploy-with-airflow-composer), [serverless functions](./walkthroughs/deploy-a-pipeline/deploy-with-google-cloud-functions), or any other cloud deployment of your choice.
- data_load_tool automates pipeline maintenance with [schema evolution](./general-usage/schema-evolution) and [schema and data contracts](./general-usage/schema-contracts).

To get started with data_load_tool, install the library using pip:

```sh
pip install data_load_tool
```
:::tip
We recommend using a clean virtual environment for your experiments! Read the [detailed instructions](./reference/installation) on how to set up one.
:::

## Load data with data_load_tool from …

<Tabs
  groupId="source-type"
  defaultValue="rest-api"
  values={[
    {"label": "REST APIs", "value": "rest-api"},
    {"label": "SQL databases", "value": "sql-database"},
    {"label": "Cloud storages or files", "value": "filesystem"},
    {"label": "Python data structures", "value": "python-data"},
]}>
  <TabItem value="rest-api">

Use data_load_tool's [REST API source](./tutorial/rest-api) to extract data from any REST API. Define the API endpoints you’d like to fetch data from, the pagination method, and authentication, and data_load_tool will handle the rest:

```py
import data_load_tool
from data_load_tool.sources.rest_api import rest_api_source

source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
        "auth": {
            "token": data_load_tool.secrets["your_api_token"],
        },
        "paginator": {
            "type": "json_link",
            "next_url_path": "paging.next",
        },
    },
    "resources": ["posts", "comments"],
})

pipeline = data_load_tool.pipeline(
    pipeline_name="rest_api_example",
    destination="duckdb",
    dataset_name="rest_api_data",
)

load_info = pipeline.run(source)

# print load info and posts table as dataframe
print(load_info)
print(pipeline.dataset().posts.df())
```

Follow the [REST API source tutorial](./tutorial/rest-api) to learn more about the source configuration and pagination methods.
  </TabItem>
  <TabItem value="sql-database">

Use the [SQL source](./tutorial/sql-database) to extract data from databases like PostgreSQL, MySQL, SQLite, Oracle, and more.

```py
from data_load_tool.sources.sql_database import sql_database

source = sql_database(
    "mysql+pymysql://rfamro@mysql-rfam-public.ebi.ac.uk:4497/Rfam"
)

pipeline = data_load_tool.pipeline(
    pipeline_name="sql_database_example",
    destination="duckdb",
    dataset_name="sql_data",
)

load_info = pipeline.run(source)

# print load info and the "family" table as dataframe
print(load_info)
print(pipeline.dataset().family.df())
```

Follow the [SQL source tutorial](./tutorial/sql-database) to learn more about the source configuration and supported databases.

  </TabItem>
  <TabItem value="filesystem">

The [Filesystem](./tutorial/filesystem) source extracts data from AWS S3, Google Cloud Storage, Google Drive, Azure, or a local file system.

```py
from data_load_tool.sources.filesystem import filesystem

resource = filesystem(
    bucket_url="s3://example-bucket",
    file_glob="*.csv"
)

pipeline = data_load_tool.pipeline(
    pipeline_name="filesystem_example",
    destination="duckdb",
    dataset_name="filesystem_data",
)

load_info = pipeline.run(resource)

# print load info and the "example" table as dataframe
print(load_info)
print(pipeline.dataset().example.df())
```

Follow the [filesystem source tutorial](./tutorial/filesystem) to learn more about the source configuration and supported storage services.

  </TabItem>
  <TabItem value="python-data">

data_load_tool is able to load data from Python generators or directly from Python data structures:

```py
import data_load_tool

@data_load_tool.resource(table_name="foo_data")
def foo():
    for i in range(10):
        yield {"id": i, "name": f"This is item {i}"}

pipeline = data_load_tool.pipeline(
    pipeline_name="python_data_example",
    destination="duckdb",
)

load_info = pipeline.run(foo)

# print load info and the "foo_data" table as dataframe
print(load_info)
print(pipeline.dataset().foo_data.df())
```

Check out the [Python data structures tutorial](./tutorial/load-data-from-an-api) to learn about data_load_tool fundamentals and advanced usage scenarios.

  </TabItem>

</Tabs>

:::tip
If you'd like to try out data_load_tool without installing it on your machine, check out the [Google Colab demo](https://colab.research.google.com/drive/1NfSB1DpwbbHX9_t5vlalBTf13utwpMGx?usp=sharing).
:::

## Join the data_load_tool community

1. Give the library a ⭐ and check out the code on [GitHub](https://github.com/dlt-hub/data_load_tool).
1. Ask questions and share how you use the library on [Slack](https://dlthub.com/community).
1. Report problems and make feature requests [here](https://github.com/dlt-hub/data_load_tool/issues/new/choose).

