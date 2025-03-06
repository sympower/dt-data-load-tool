import data_load_tool


@data_load_tool.resource
def example_resource(api_url=data_load_tool.config.value, api_key=data_load_tool.secrets.value, last_id=0):
    yield [api_url, api_key, str(last_id), "param4", "param5"]


@data_load_tool.source
def example_source(api_url=data_load_tool.config.value, api_key=data_load_tool.secrets.value, last_id=0):
    # return all the resources to be loaded
    return example_resource(api_url, api_key, last_id)


if __name__ == "__main__":
    p = data_load_tool.pipeline(pipeline_name="dummy_pipeline", destination="dummy")
    load_info = p.run(example_source(last_id=819273998))
    print(load_info)
