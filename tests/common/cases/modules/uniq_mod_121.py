import inspect
from data_load_tool.common.utils import get_module_name


def find_my_module():
    pass


if __name__ == "__main__":
    print(get_module_name(inspect.getmodule(find_my_module)))
