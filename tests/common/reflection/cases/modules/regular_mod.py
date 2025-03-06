import data_load_tool


@data_load_tool.source
def s():
    return []


def f():
    pass


@data_load_tool.resource(standalone=True)
def r():
    yield [1, 2, 3]
