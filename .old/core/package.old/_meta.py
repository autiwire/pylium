from abc import ABC

class _PyliumMeta(ABC.__class__, type):
    """
    This is the base meta-class for all Pylium packages.
    """
    def __new__(mcls, name, bases, namespace, **kwargs):
        print(f"Meta module: {mcls.__module__}")
        return super().__new__(mcls, name, bases, namespace, **kwargs)

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace)

