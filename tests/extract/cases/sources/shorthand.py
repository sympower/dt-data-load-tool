import data_load_tool


@data_load_tool.source
def shorthand(data):
    return data_load_tool.resource(data, name="alpha")


@data_load_tool.source(name="shorthand_registry", section="shorthand")
def with_shorthand_registry(data):
    return data_load_tool.resource(data, name="alpha")
