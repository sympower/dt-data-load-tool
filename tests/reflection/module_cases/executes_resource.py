import data_load_tool


@data_load_tool.resource
def aleph(n: int):
    for i in range(0, n):
        yield i


print(list(aleph(10)))
