import inspect

import data_load_tool
import data_load_tool.destinations
from data_load_tool import pipeline, attach, run, source, resource, transformer

DLT = data_load_tool.__name__
DESTINATIONS = data_load_tool.destinations.__name__
PIPELINE = pipeline.__name__
ATTACH = attach.__name__
RUN = run.__name__
SOURCE = source.__name__
RESOURCE = resource.__name__
TRANSFORMER = transformer.__name__

DETECTED_FUNCTIONS = [PIPELINE, SOURCE, RESOURCE, RUN, TRANSFORMER]
SIGNATURES = {
    PIPELINE: inspect.signature(pipeline),
    ATTACH: inspect.signature(attach),
    RUN: inspect.signature(run),
    SOURCE: inspect.signature(source),
    RESOURCE: inspect.signature(resource),
    TRANSFORMER: inspect.signature(transformer),
}
