# Project

import Link from '../../_plus_admonition.md';

<Link/>

A data_load_tool+ Project offers developers a declarative approach for defining data workflow components: sources, destinations, pipelines, transformations, parameters, etc. It follows an opinionated structure centered around a Python manifest file `data_load_tool.yml`, where all data_load_tool entities are defined in an organized way. The manifest file acts like a single source of truth for data pipelines, keeping all teams aligned.

The project layout has the following components:

1. A data_load_tool manifest file (`data_load_tool.yml`) which specifies data platform entities like sources, destinations, pipelines, transformations, etc.
2. `.data_load_tool` folder with secrets and other information, backward compatible with OSS `data_load_tool`
3. Python modules with source code and tests. We propose a strict layout of the modules (i.e., source code is in the `sources/` folder, etc.)
4. `_data` folder (excluded from `.git`) where pipeline working directories and local destination files (i.e., filesystem, duckdb databases) are kept.

A general data_load_tool+ project has the following structure:

```text
.
├── .data_load_tool/                 # your data_load_tool settings including profile settings
│   ├── config.toml
│   ├── dev.secrets.toml
│   └── secrets.toml
├── _data/             # local storage for your project, excluded from git
├── sources/              # your sources, contains the code for the arrow source
│   └── arrow.py
├── .gitignore
├── requirements.txt
└── data_load_tool.yml               # the main project manifest
```

Read more about data_load_tool+ Project in the [project feature description](../features/projects.md)

:::note
To get started with a data_load_tool+ Project and learn how to manage it using cli commands, check out our [tutorial](../getting-started/tutorial.md).
:::
