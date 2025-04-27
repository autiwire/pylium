from .__header__ import Package

class PackageImpl(Package):
    def __init__(self):
        super().__init__()

    def test(self):
        print("test OK !")