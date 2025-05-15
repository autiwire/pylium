from ._h import *

class PyliumPackageImpl(Package):
    """
    Pylium package implementation
    """
    authors: ClassVar[List[Package.AuthorInfo]] = [
        Package.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=Package.Date(2025, 5, 14))
    ]
    changelog: ClassVar[List[Package.ChangelogEntry]] = [
        Package.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=Package.Date(2025, 5, 14)),
    ]

logger = PyliumPackageImpl.logger

class PyliumImpl(Pylium):
    """
    Pylium implementation
    """

    _is_impl = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.debug(f"Initializing Pylium: {self.name}")
