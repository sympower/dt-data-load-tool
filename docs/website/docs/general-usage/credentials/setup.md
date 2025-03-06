---
title: How to set up credentials
description: Where and in which order data_load_tool looks for config/secrets.
keywords: [credentials, secrets.toml, secrets, config, configuration, environment
      variables, provider]
---

`data_load_tool` automatically extracts configuration settings and secrets based on flexible [naming conventions](#naming-convention).

It then [injects](advanced/#injection-mechanism) these values where needed in functions decorated with `@data_load_tool.source`, `@data_load_tool.resource`, or `@data_load_tool.destination`.

:::note
* **Configuration** refers to non-sensitive settings that define a data pipeline's behavior. These include file paths, database hosts, timeouts, API URLs, and performance settings.
* **Secrets** are sensitive data like passwords, API keys, and private keys. They should never be hard-coded to avoid security risks.
:::

## Available config providers

:::tip data_load_tool+
To define your configuration (including sources, destinations, pipeline and parameters) in a declarative way in the YAML file, check out [data_load_tool+](../../plus/features/projects.md).
:::

There are multiple ways to define configurations and credentials for your pipelines. `data_load_tool` looks for these definitions in the following order during pipeline execution:

1. [Environment Variables](#environment-variables): If a value for a specific argument is found in an environment variable, data_load_tool will use it and will not proceed to search in lower-priority providers.

1. [Vaults](#vaults): Credentials specified in vaults like Google Secrets Manager, Azure Key Vault, AWS Secrets Manager.

1. [secrets.toml and config.toml files](#secretstoml-and-configtoml): These files are used for storing both configuration values and secrets. `secrets.toml` is dedicated to sensitive information, while `config.toml` contains non-sensitive configuration data.

1. [Custom Providers](#custom-providers) added with `register_provider`: This is a custom provider implementation you can design yourself.
A custom config provider is helpful if you want to use your own configuration file structure or perform advanced preprocessing of configs and secrets.

1. [Default Argument Values](./advanced#injection-mechanism): These are the values specified in the function's signature.

:::tip
Please make sure your pipeline name contains no whitespace or any other punctuation characters except `"-"` and `"_"`. This way, you will ensure your code is working with any configuration option.
:::

## Naming convention

`data_load_tool` uses a specific naming hierarchy to search for the secrets and config values. This makes configurations and secrets easy to manage.

To keep the naming convention flexible, `data_load_tool` looks for a lot of possible combinations of key names, starting from the most specific possible path. Then, if the value is not found, it removes the right-most section and tries again.

The most specific possible path for **sources** looks like:

<Tabs
  groupId="config-provider-type"
  defaultValue="toml"
  values={[
    {"label": "TOML config provider", "value": "toml"},
    {"label": "Environment variables", "value": "env"},
    {"label": "In the code", "value": "code"},
]}>
  <TabItem value="toml">

```sh
[<pipeline_name>.sources.<source_module_name>.<source_function_name>]
<argument_name>="some_value"
```
  </TabItem>
  <TabItem value="env">

```sh
export PIPELINE_NAME__SOURCES__SOURCE_MODULE_NAME__SOURCE_FUNCTION_NAME__ARGUMENT_NAME="some_value"
```
  </TabItem>
  <TabItem value="code">

```py
import os

os.environ["PIPELINE_NAME__SOURCES__SOURCE_MODULE_NAME__SOURCE_FUNCTION_NAME__ARGUMENT_NAME"] = "some_value"
```
  </TabItem>
</Tabs>

The most specific possible path for **destinations** looks like:

<Tabs
  groupId="config-provider-type"
  defaultValue="toml"
  values={[
    {"label": "TOML config provider", "value": "toml"},
    {"label": "Environment variables", "value": "env"},
    {"label": "In the code", "value": "code"},
]}>
  <TabItem value="toml">

```sh
[<pipeline_name>.destination.<destination_name>.credentials]
<credential_option>="some_value"
```
  </TabItem>
  <TabItem value="env">

```sh
export PIPELINE_NAME__DESTINATION__DESTINATION_NAME__CREDENTIALS__CREDENTIAL_VALUE="some_value"
```
  </TabItem>
  <TabItem value="code">

```py
import os

os.environ["PIPELINE_NAME__DESTINATION__DESTINATION_NAME__CREDENTIALS__CREDENTIAL_VALUE"] = "some_value"
```
  </TabItem>
</Tabs>

### Example

For example, if the source module is named `pipedrive` and the source is defined as follows:

```py
# pipedrive.py

@data_load_tool.source
def deals(api_key: str = data_load_tool.secrets.value):
    pass
```

`data_load_tool` will search for the following names in this order:

1. `sources.pipedrive.deals.api_key`
2. `sources.pipedrive.api_key`
3. `sources.api_key`
4. `api_key`

:::tip
You can use your pipeline name to have separate configurations for each pipeline in your project. All config values will be looked at with the pipeline name first and then again without it.

```toml
[pipeline_name_1.sources.google_sheets.credentials]
client_email = "<client_email_1>"
private_key = "<private_key_1>"
project_id = "<project_id_1>"

[pipeline_name_2.sources.google_sheets.credentials]
client_email = "<client_email_2>"
private_key = "<private_key_2>"
project_id = "<project_id_2>"
```
:::

### Credential types

In most cases, credentials are just key-value pairs, but in some cases, the actual structure of [credentials](./complex_types) could be quite complex and support several ways of setting it up.
For example, to connect to a `sql_database` source, you can either set up a connection string:

```toml
[sources.sql_database]
credentials="snowflake://user:password@service-account/database?warehouse=warehouse_name&role=role"
```
or set up all parameters of connection separately:

```toml
[sources.sql_database.credentials]
drivername="snowflake"
username="user"
password="password"
database="database"
host="service-account"
warehouse="warehouse_name"
role="role"
```

`data_load_tool` can work with both ways and convert one to another. To learn more about which credential types are supported, visit the [complex credential types](./complex_types) page.

## Environment variables

`data_load_tool` prioritizes security by looking in environment variables before looking into the .toml files.

The format of lookup keys is slightly different from secrets files because for environment variables, all names are capitalized, and sections are separated with a double underscore `"__"`. For example, to specify the Facebook Ads access token through environment variables, you would need to set up:

```sh
export SOURCES__FACEBOOK_ADS__ACCESS_TOKEN="<access_token>"
```

Check out the [example](#examples) of setting up credentials through environment variables.

:::tip
To organize development and securely manage environment variables for credentials storage, you can use [python-dotenv](https://pypi.org/project/python-dotenv/) to automatically load variables from an `.env` file.
:::

:::tip
Environment Variables additionally looks for secret values in `/run/secrets/<secret-name>` to seamlessly resolve values defined as **Kubernetes/Docker secrets**.
For that purpose it uses alternative name format with lowercase, `-` (dash) as a separator and "_" converted into `-`:
In the example above: `sources--facebook-ads--access-token` will be used to search for the secrets (and other forms up until `access-token`).
Mind that only values marked as secret (with `data_load_tool.secrets.value` or using ie. `TSecretStrValue` explicitly) are checked. Remember to name your secrets
in Kube resources/compose file properly.
:::

## Vaults

Vault integration methods vary based on the vault type. Check out our example involving [Google Cloud Secrets Manager](../../walkthroughs/add_credentials.md#retrieving-credentials-from-google-cloud-secret-manager).
For other vault integrations, you are welcome to [contact sales](https://dlthub.com/contact-sales) to learn about our [building blocks for data platform teams](https://dlthub.com/product/data-platform-teams#secure).

## secrets.toml and config.toml

The TOML config provider in `data_load_tool` utilizes two TOML files:

`config.toml`:

- Configs refer to non-sensitive configuration data. These are settings, parameters, or options that define the behavior of a data pipeline.
- They can include things like file paths, database hosts and timeouts, API URLs, performance settings, or any other settings that affect the pipeline's behavior.
- Accessible in code through `data_load_tool.config.values`

`secrets.toml`:

- Secrets are sensitive information that should be kept confidential, such as passwords, API keys, private keys, and other confidential data.
- It's crucial to never hard-code secrets directly into the code, as it can pose a security risk.
- Accessible in code through `data_load_tool.secrets.values`

By default, the `.gitignore` file in the project prevents `secrets.toml` from being added to version control and pushed. However, `config.toml` can be freely added to version control.

### Location

The TOML provider always loads those files from the `.data_load_tool` folder, located **relative** to the current working directory.

For example, if your working directory is `my_dlt_project` and your project has the following structure:

```text
my_dlt_project:
  |
  pipelines/
    |---- .data_load_tool/secrets.toml
    |---- google_sheets.py
```

and you run
```sh
python pipelines/google_sheets.py
```
then `data_load_tool` will look for secrets in `my_dlt_project/.data_load_tool/secrets.toml` and ignore the existing `my_dlt_project/pipelines/.data_load_tool/secrets.toml`.

If you change your working directory to `pipelines` and run
```sh
python google_sheets.py
```

`data_load_tool` will look for `my_dlt_project/pipelines/.data_load_tool/secrets.toml` as (probably) expected.

:::caution
The TOML provider also has the capability to read files from `~/.data_load_tool/` (located in the user's home directory) in addition to the local project-specific `.data_load_tool` folder.
:::

### Structure

`data_load_tool` organizes sections in TOML files in a specific structure required by the [injection mechanism](advanced/#injection-mechanism).
Understanding this structure gives you more flexibility in setting credentials. For more details, see [TOML files structure](advanced/#toml-files-structure).

## Custom providers

You can use the `CustomLoaderDocProvider` classes to supply a custom dictionary to `data_load_tool` for use
as a supplier of `config` and `secret` values. The code below demonstrates how to use a config stored in `config.json`.

```py
import data_load_tool
from data_load_tool.common.configuration.providers import CustomLoaderDocProvider

# Create a function that loads a dict
def load_config():
    with open("config.json", "rb") as f:
        return json.load(f)


# Create the custom provider
provider = CustomLoaderDocProvider("my_json_provider", load_config)

# Register provider
data_load_tool.config.register_provider(provider)
```

:::tip
Check out an [example](../../examples/custom_config_provider) for a YAML based config provider that supports switchable profiles.
:::

## Examples

### Setup both configurations and secrets

`data_load_tool` recognizes two types of data: secrets and configurations. The main difference is that secrets contain sensitive information,
while configurations hold non-sensitive information and can be safely added to version control systems like git.
This means you have more flexibility with configurations. You can set up configurations directly in the code,
but it is strongly advised not to do this with secrets.

:::caution
You can put all configurations and credentials in the `secrets.toml` if it's more convenient.
However, credentials cannot be placed in `configs.toml` because `data_load_tool` doesn't look for them there.
:::

Let's assume we have a [notion](../../dlt-ecosystem/verified-sources/notion) source and [filesystem](../../dlt-ecosystem/destinations/filesystem) destination:

<Tabs
  groupId="config-provider-type"
  defaultValue="toml"
  values={[
    {"label": "TOML config provider", "value": "toml"},
    {"label": "Environment variables", "value": "env"},
    {"label": "In the code", "value": "code"},
]}>

  <TabItem value="toml">

```toml
# we can set up a lot in config.toml
# config.toml
[runtime]
log_level="INFO"

[destination.filesystem]
bucket_url = "s3://[your_bucket_name]"

[normalize.data_writer]
disable_compression=true

# but credentials should go to secrets.toml!
# secrets.toml
[source.notion]
api_key = "api_key"

[destination.filesystem.credentials]
aws_access_key_id = "ABCDEFGHIJKLMNOPQRST" # copy the access key here
aws_secret_access_key = "1234567890_access_key" # copy the secret access key here
```

  </TabItem>

  <TabItem value="env">

```sh
# Environment variables are set up the same way both for configs and secrets
export RUNTIME__LOG_LEVEL="INFO"
export DESTINATION__FILESYSTEM__BUCKET_URL="s3://[your_bucket_name]"
export NORMALIZE__DATA_WRITER__DISABLE_COMPRESSION="true"
export SOURCE__NOTION__API_KEY="api_key"
export DESTINATION__FILESYSTEM__CREDENTIALS__AWS_ACCESS_KEY_ID="ABCDEFGHIJKLMNOPQRST"
export DESTINATION__FILESYSTEM__CREDENTIALS__AWS_SECRET_ACCESS_KEY="1234567890_access_key"
```

  </TabItem>

  <TabItem value="code">

```py
import os
import data_load_tool
import botocore.session
from data_load_tool.common.credentials import AwsCredentials

# you can freely set up configuration directly in the code

# via env vars
os.environ["RUNTIME__LOG_LEVEL"] = "INFO"
os.environ["DESTINATION__FILESYSTEM__BUCKET_URL"] = "s3://[your_bucket_name]"
os.environ["NORMALIZE__DATA_WRITER__DISABLE_COMPRESSION"] = "true"

# or even directly to the data_load_tool.config
data_load_tool.config["runtime.log_level"] = "INFO"
data_load_tool.config["destination.filesystem.bucket_url"] = "s3://[your_bucket_name]"
data_load_tool.config["normalize.data_writer.disable_compression"] = "true"

# but please, do not set up the secrets in the code!
# what you can do is reassign env variables:
os.environ["SOURCE__NOTION__API_KEY"] = os.environ.get("NOTION_KEY")

# or use a third-party credentials supplier
credentials = AwsCredentials()
session = botocore.session.get_session()
credentials.parse_native_representation(session)
data_load_tool.secrets["destination.filesystem.credentials"] = credentials
```

  </TabItem>

</Tabs>


### Google credentials for both source and destination

Let's assume we use the `bigquery` destination and the `google_sheets` source. They both use Google credentials and expect them to be configured under the `credentials` key.

1. If we create just a single `credentials` section, the destination and source will share the same credentials.

<Tabs
  groupId="config-provider-type"
  defaultValue="toml"
  values={[
    {"label": "TOML config provider", "value": "toml"},
    {"label": "Environment variables", "value": "env"},
    {"label": "In the code", "value": "code"},
]}>

  <TabItem value="toml">

```toml
[credentials]
client_email = "<client_email_both_for_destination_and_source>"
private_key = "<private_key_both_for_destination_and_source>"
project_id = "<project_id_both_for_destination_and_source>"
```

  </TabItem>

  <TabItem value="env">

```sh
export CREDENTIALS__CLIENT_EMAIL="<client_email_both_for_destination_and_source>"
export CREDENTIALS__PRIVATE_KEY="<private_key_both_for_destination_and_source>"
export CREDENTIALS__PROJECT_ID="<project_id_both_for_destination_and_source>"
```

  </TabItem>

 <TabItem value="code">

```py
import os

# Do not set up the secrets directly in the code!
# What you can do is reassign env variables.
os.environ["CREDENTIALS__CLIENT_EMAIL"] = os.environ.get("GOOGLE_CLIENT_EMAIL")
os.environ["CREDENTIALS__PRIVATE_KEY"] = os.environ.get("GOOGLE_PRIVATE_KEY")
os.environ["CREDENTIALS__PROJECT_ID"] = os.environ.get("GOOGLE_PROJECT_ID")
```

  </TabItem>

</Tabs>

2. If we define sections as below, we'll keep the credentials separate

<Tabs
  groupId="config-provider-type"
  defaultValue="toml"
  values={[
    {"label": "TOML config provider", "value": "toml"},
    {"label": "Environment variables", "value": "env"},
    {"label": "In the code", "value": "code"},
]}>

  <TabItem value="toml">

```toml
# Google Sheet credentials
[sources.credentials]
client_email = "<client_email from services.json>"
private_key = "<private_key from services.json>"
project_id = "<project_id from services json>"

# BigQuery credentials
[destination.credentials]
client_email = "<client_email from services.json>"
private_key = "<private_key from services.json>"
project_id = "<project_id from services json>"
```

  </TabItem>

  <TabItem value="env">

```sh
# Google Sheet credentials
export SOURCES__CREDENTIALS__CLIENT_EMAIL="<client_email>"
export SOURCES__CREDENTIALS__PRIVATE_KEY="<private_key>"
export SOURCES__CREDENTIALS__PROJECT_ID="<project_id>"

# BigQuery credentials
export DESTINATION__CREDENTIALS__CLIENT_EMAIL="<client_email>"
export DESTINATION__CREDENTIALS__PRIVATE_KEY="<private_key>"
export DESTINATION__CREDENTIALS__PROJECT_ID="<project_id>"
```

  </TabItem>

 <TabItem value="code">

```py
import data_load_tool
import os

# Do not set up the secrets directly in the code!
# What you can do is reassign env variables.
os.environ["DESTINATION__CREDENTIALS__CLIENT_EMAIL"] = os.environ.get("BIGQUERY_CLIENT_EMAIL")
os.environ["DESTINATION__CREDENTIALS__PRIVATE_KEY"] = os.environ.get("BIGQUERY_PRIVATE_KEY")
os.environ["DESTINATION__CREDENTIALS__PROJECT_ID"] = os.environ.get("BIGQUERY_PROJECT_ID")

# Or set them to the data_load_tool.secrets.
data_load_tool.secrets["sources.credentials.client_email"] = os.environ.get("SHEETS_CLIENT_EMAIL")
data_load_tool.secrets["sources.credentials.private_key"] = os.environ.get("SHEETS_PRIVATE_KEY")
data_load_tool.secrets["sources.credentials.project_id"] = os.environ.get("SHEETS_PROJECT_ID")
```

  </TabItem>

</Tabs>

Now `data_load_tool` looks for destination credentials in the following order:
```sh
destination.bigquery.credentials --> Not found
destination.credentials --> Found
```

When looking for the source credentials:
```sh
sources.google_sheets_module.google_sheets_function.credentials --> Not found
sources.google_sheets_function.credentials --> Not found
sources.credentials --> Found
```

### Credentials for several different sources and destinations

Let's assume we have several different Google sources and destinations. We can use full paths to organize the `secrets.toml` file:

<Tabs
  groupId="config-provider-type"
  defaultValue="toml"
  values={[
    {"label": "TOML config provider", "value": "toml"},
    {"label": "Environment variables", "value": "env"},
    {"label": "In the code", "value": "code"},
]}>

  <TabItem value="toml">

```toml
# Google Sheet credentials
[sources.google_sheets.credentials]
client_email = "<client_email from services.json>"
private_key = "<private_key from services.json>"
project_id = "<project_id from services.json>"

# Google Analytics credentials
[sources.google_analytics.credentials]
client_email = "<client_email from services.json>"
private_key = "<private_key from services.json>"
project_id = "<project_id from services.json>"

# BigQuery credentials
[destination.bigquery.credentials]
client_email = "<client_email from services.json>"
private_key = "<private_key from services.json>"
project_id = "<project_id from services.json>"
```

  </TabItem>

  <TabItem value="env">

```sh
# Google Sheet credentials
export SOURCES__GOOGLE_SHEETS__CREDENTIALS__CLIENT_EMAIL="<client_email>"
export SOURCES__GOOGLE_SHEETS__CREDENTIALS__PRIVATE_KEY="<private_key>"
export SOURCES__GOOGLE_SHEETS__CREDENTIALS__PROJECT_ID="<project_id>"

# Google Analytics credentials
export SOURCES__GOOGLE_ANALYTICS__CREDENTIALS__CLIENT_EMAIL="<client_email>"
export SOURCES__GOOGLE_ANALYTICS__CREDENTIALS__PRIVATE_KEY="<private_key>"
export SOURCES__GOOGLE_ANALYTICS__CREDENTIALS__PROJECT_ID="<project_id>"

# BigQuery credentials
export DESTINATION__BIGQUERY__CREDENTIALS__CLIENT_EMAIL="<client_email>"
export DESTINATION__BIGQUERY__CREDENTIALS__PRIVATE_KEY="<private_key>"
export DESTINATION__BIGQUERY__CREDENTIALS__PROJECT_ID="<project_id>"
```

  </TabItem>

 <TabItem value="code">

```py
import os
import data_load_tool

# Do not set up the secrets directly in the code!
# What you can do is reassign env variables
os.environ["SOURCES__GOOGLE_ANALYTICS__CREDENTIALS__CLIENT_EMAIL"] = os.environ.get("SHEETS_CLIENT_EMAIL")
os.environ["SOURCES__GOOGLE_ANALYTICS__CREDENTIALS__PRIVATE_KEY"] = os.environ.get("ANALYTICS_PRIVATE_KEY")
os.environ["SOURCES__GOOGLE_ANALYTICS__CREDENTIALS__PROJECT_ID"] = os.environ.get("ANALYTICS_PROJECT_ID")

os.environ["DESTINATION__CREDENTIALS__CLIENT_EMAIL"] = os.environ.get("BIGQUERY_CLIENT_EMAIL")
os.environ["DESTINATION__CREDENTIALS__PRIVATE_KEY"] = os.environ.get("BIGQUERY_PRIVATE_KEY")
os.environ["DESTINATION__CREDENTIALS__PROJECT_ID"] = os.environ.get("BIGQUERY_PROJECT_ID")

# Or set them to the data_load_tool.secrets
data_load_tool.secrets["sources.credentials.client_email"] = os.environ.get("SHEETS_CLIENT_EMAIL")
data_load_tool.secrets["sources.credentials.private_key"] = os.environ.get("SHEETS_PRIVATE_KEY")
data_load_tool.secrets["sources.credentials.project_id"] = os.environ.get("SHEETS_PROJECT_ID")
```

  </TabItem>

</Tabs>

### Credentials for several sources of the same type

Let's assume we have several sources of the same type. How can we separate them in the `secrets.toml`? The recommended solution is to use different pipeline names for each source:

<Tabs
  groupId="config-provider-type"
  defaultValue="toml"
  values={[
    {"label": "TOML config provider", "value": "toml"},
    {"label": "Environment variables", "value": "env"},
    {"label": "In the code", "value": "code"},
]}>

  <TabItem value="toml">

```toml
[pipeline_name_1.sources.sql_database]
credentials="snowflake://user1:password1@service-account/database1?warehouse=warehouse_name&role=role1"

[pipeline_name_2.sources.sql_database]
credentials="snowflake://user2:password2@service-account/database2?warehouse=warehouse_name&role=role2"
```

  </TabItem>

  <TabItem value="env">

```sh
export PIPELINE_NAME_1_SOURCES__SQL_DATABASE__CREDENTIALS="snowflake://user1:password1@service-account/database1?warehouse=warehouse_name&role=role1"
export PIPELINE_NAME_2_SOURCES__SQL_DATABASE__CREDENTIALS="snowflake://user2:password2@service-account/database2?warehouse=warehouse_name&role=role2"
```

  </TabItem>

 <TabItem value="code">

```py
import os
import data_load_tool

# Do not set up the secrets directly in the code!
# What you can do is reassign env variables
os.environ["PIPELINE_NAME_1_SOURCES__SQL_DATABASE__CREDENTIALS"] = os.environ.get("SQL_CREDENTIAL_STRING_1")

# Or set them to the data_load_tool.secrets
data_load_tool.secrets["pipeline_name_2.sources.sql_database.credentials"] = os.environ.get("SQL_CREDENTIAL_STRING_2")
```

  </TabItem>

</Tabs>

## Understanding the exceptions

If `data_load_tool` expects a configuration of secrets value but cannot find it, it will output the `ConfigFieldMissingException`.

Let's run the `chess.py` example without providing the password:

```sh
$ CREDENTIALS="postgres://loader@localhost:5432/dlt_data" python chess.py
...
data_load_tool.common.configuration.exceptions.ConfigFieldMissingException: Following fields are missing: ['password'] in configuration with spec PostgresCredentials
        for field "password" config providers and keys were tried in the following order:
                In Environment Variables key CHESS_GAMES__DESTINATION__POSTGRES__CREDENTIALS__PASSWORD was not found.
                In Environment Variables key CHESS_GAMES__DESTINATION__CREDENTIALS__PASSWORD was not found.
                In Environment Variables key CHESS_GAMES__CREDENTIALS__PASSWORD was not found.
                In secrets.toml key chess_games.destination.postgres.credentials.password was not found.
                In secrets.toml key chess_games.destination.credentials.password was not found.
                In secrets.toml key chess_games.credentials.password was not found.
                In Environment Variables key DESTINATION__POSTGRES__CREDENTIALS__PASSWORD was not found.
                In Environment Variables key DESTINATION__CREDENTIALS__PASSWORD was not found.
                In Environment Variables key CREDENTIALS__PASSWORD was not found.
                In secrets.toml key destination.postgres.credentials.password was not found.
                In secrets.toml key destination.credentials.password was not found.
                In secrets.toml key credentials.password was not found.
Please refer to https://dlthub.com/docs/general-usage/credentials/ for more information
```

It tells you exactly which paths `data_load_tool` looked at, via which config providers and in which order.

In the example above:

1. First, `data_load_tool` looked in a big section `chess_games`, which is the name of the pipeline.
2. In each case, it starts with full paths and goes to the minimum path `credentials.password`.
3. First, it looks into environment variables, then in `secrets.toml`. It displays the exact keys tried.
4. Note that `config.toml` was skipped! It could not contain any secrets.

