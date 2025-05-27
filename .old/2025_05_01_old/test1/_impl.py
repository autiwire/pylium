from ._header import Test1
from pylium.core.package import Package

class _Test1(Package.Impl, Test1, table=False):
    """
    This is the implementation of the Test1 component.
    """
    #test_fieldx: str = Package.Header.Field(default="testx", primary_key=True)

    def __init__(self):
        print(f"_Test1 init: {self.__module__}")
        super().__init__()
        
