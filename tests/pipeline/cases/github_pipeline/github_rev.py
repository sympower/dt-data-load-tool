import data_load_tool


@data_load_tool.source
def github():
    @data_load_tool.resource(
        table_name="issues__2",
        primary_key="id",
    )
    def load_issues():
        # return data with path separators
        yield [
            {
                "id": 100,
                "issue__id": 10,
            }
        ]

    return load_issues


if __name__ == "__main__":
    p = data_load_tool.pipeline("dlt_github_pipeline", destination="duckdb", dataset_name="github_3")
    github_source = github()
    info = p.run(github_source)
    print(info)
