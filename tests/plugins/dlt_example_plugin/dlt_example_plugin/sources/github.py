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
