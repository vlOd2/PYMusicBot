import os

__all__ = []

# Add all modules into __all__ so we can easily import everything
for module_file in os.listdir(os.path.dirname(__file__)):
    if module_file[-3:] != ".py" or module_file == "__init__.py": continue
    __all__.append(module_file[:-3])