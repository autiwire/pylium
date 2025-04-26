from pylium.core import Package

class Test1(Package.Header, table=True):
    """
    This is the header class for Pylium.
    """

    test_field: str = Package.Header.Field(default="test", primary_key=True)

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return f"YYYY {self.__class__.__name__}()"
