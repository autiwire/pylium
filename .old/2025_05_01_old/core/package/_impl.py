from ._component import _PackageImplComponentMixin

class _PackageImplMixin(_PackageImplComponentMixin):
    """
    This is the base class for all Pylium implementation classes.
    """

    # *** subclass overrides ***

    # The name of the component - used to register the component (set once per inheritance hierarchy)
    __component__ = "impl"

    __abstract__ = True

    pass

_PackageImplMixin.register()