---
title: "Local transformations"
description: Run local transformations with data_load_tool+ Cache
keywords: ["data_load_tool+", "transformations", "cache", "dbt"]
---
import DocCardList from '@theme/DocCardList';
import Link from '../../../_plus_admonition.md';

<Link/>

As part of data_load_tool+, we provide a local transformation [cache](../../core-concepts/cache.md) — a staging layer for data transformations allowing you to test, validate, and debug data pipelines without running everything in the warehouse. With local transformations, you can:

* Run transformations locally, eliminating the need to wait for warehouse queries.
* Validate the schema before loading to catch mismatches early.
* Test without incurring cloud costs, as in-memory execution prevents wasted compute.

Local transformations are built on DuckDB, Arrow, and dbt, so they work with your existing stack.

:::caution
The local transformations feature is currently in the early access phase. We recommend waiting for general access before using it in production.
:::

<DocCardList />

