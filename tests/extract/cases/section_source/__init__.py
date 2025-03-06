import data_load_tool


@data_load_tool.source
def init_source_f_1(val: str = data_load_tool.config.value):
    return data_load_tool.resource([val], name="f_1")


@data_load_tool.resource
def init_resource_f_2(val: str = data_load_tool.config.value):
    yield [val]
