---
title: Profiles
keywords: [data_load_tool+, profiles]
---

import Link from '../../_plus_admonition.md';

<Link/>

A profile is a set of configurations and secrets defined for a specific use case. Profiles provide a way to manage different configurations for different environments.

They are defined in the `data_load_tool.yml` under the `profiles` section.

```yaml
profiles:
  # profiles allow you to configure different settings for different environments
  dev:
    sources:
      my_arrow_source:
        row_count: 100
    runtime:
      log_level: DEBUG
  prod:
    sources:
      my_arrow_source:
        row_count: 200
    runtime:
      log_level: INFO
    destinations:
      my_duckdb_destination:
        credentials: my_data_prod.duckdb
```

Every project includes two implicit profiles by default: `dev` and `tests`. If no profile is specified, the `dev` profile is loaded by default.
All CLI commands that run on a project support the `--profile` option, allowing you to specify the desired profile. For example,

```sh
data_load_tool project --profile dev my_pipeline run
data_load_tool dataset --profile prod my_duckdb_destination_dataset row-counts
```

## Using config files with profiles

All the configuration and secrets for profiles can also be placed in TOML files, as [described in data_load_tool OSS documentation](../../general-usage/credentials/).
Each profile can have its own `secrets.toml` file, which is only loaded when that profile is active.

For example, if you have two secrets files under `.data_load_tool`:

```sh
.
├── .data_load_tool/                 # your data_load_tool settings including profile settings
│   ├── config.toml
│   ├── dev.secrets.toml
│   └── tests.secrets.toml
```

You can run a pipeline with different profiles as follows:

```sh
data_load_tool pipeline --profile dev my_pipeline run
data_load_tool pipeline --profile tests my_pipeline run
```

:::caution
Please note the following inconsistencies between the YAML and TOML files that will be fixed in the future:

* The YAML `destinations` section is singularized to `destination` in the TOML file.
* The project variables such as `tmp_dir` are not available in the TOML files.
:::

## Pinning profiles
You can pin a profile locally, making the given profile name the default one. This is useful, for example, when deploying your project in a production or staging environment.
```sh
data_load_tool profile prod pin
```
will pin the `prod` profile and from now on all Python scripts and cli commands will see it as the default and switch to it automatically.
The profile pin is kept in the `.data_load_tool/profile-name` file. Remove this file to unpin. Note that our default `.gitignore` prevents this file from being added.

### Settings in the `data_load_tool.yml` file vs TOML files

For data_load_tool+ Projects, it's best practice to keep all non-secret settings in `data_load_tool.yml` and store secrets only in `.data_load_tool/secrets.toml`. This ensures that sensitive data is only available in the necessary profiles or environments.

In the example above, some non-secret values were moved to `.data_load_tool/secrets.toml` for demonstration purposes only - this is not the recommended approach.
