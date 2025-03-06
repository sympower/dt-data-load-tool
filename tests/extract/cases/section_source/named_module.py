import data_load_tool

__source_name__ = "name_overridden"


@data_load_tool.source(section="name_overridden")
def source_f_1(val: str = data_load_tool.config.value):
    return data_load_tool.resource([val], name="f_1")


@data_load_tool.resource
def resource_f_2(val: str = data_load_tool.config.value):
    yield [val]
