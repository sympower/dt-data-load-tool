import data_load_tool

from tests.extract.cases.section_source import init_resource_f_2
from tests.extract.cases.section_source.named_module import resource_f_2


@data_load_tool.source
def with_external(source_val: str = data_load_tool.config.value):
    @data_load_tool.resource
    def inner_resource(val):
        yield val

    return (
        data_load_tool.resource([source_val], name="source_val"),
        inner_resource(source_val),
        init_resource_f_2,
        resource_f_2,
    )


@data_load_tool.source
def with_bound_external(source_val: str = data_load_tool.config.value):
    @data_load_tool.resource
    def inner_resource(val):
        yield val

    return (
        data_load_tool.resource([source_val], name="source_val"),
        inner_resource(source_val),
        init_resource_f_2(),
        resource_f_2(),
    )
