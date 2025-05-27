class ImplMixin:
    """
    This is the implementation mixin for all Pylium components.
    """

    def __init__(self, *args, **kwargs):
        print(f"ImplMixin init: {self.__module__}|{self.__class__.__name__}")

    def __new__(cls, *args, **kwargs):
        print(f"ImplMixin new: {cls.__module__}|{cls.__class__.__name__}")
        return super().__new__(cls, *args, **kwargs)
