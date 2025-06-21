"""
License type for the manifest.
"""

# Pylium imports
from .value import ManifestValue
from .author import ManifestAuthor

# Standard library imports
from typing import Optional, List, Any, Generator

class ManifestCopyright(ManifestValue):
    def __init__(self, date: Optional[ManifestValue.Date], author: Optional[ManifestAuthor] = None):
        self.date = date
        self.author = author

    def __str__(self):
        return f"(c) ({self.date}) {self.author}"
    
    def __repr__(self):
        return f"(c) ({self.date}) {self.author}"
    

class ManifestLicense(ManifestValue):
    def __init__(self, tag: str, spdx: str, name: str, url: Optional[str] = None):
        self.tag = tag
        self.spdx = spdx
        self.name = name
        self.url = url

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestLicense):
            return False
        return self.tag == other.tag
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self):
        return f"{self.tag} ({self.spdx}) {self.name} [{self.url}]"
    
    def __repr__(self):
        return f"{self.tag} ({self.spdx}) {self.name} [{self.url}]"
    

class ManifestLicenseList(ManifestValue):
    def __init__(self, licenses: List[ManifestLicense]):
        self._licenses = licenses

    def __getattr__(self, tag: str) -> ManifestLicense:        
        for license in self._licenses:
            if license.tag == tag:
                return license
        raise AttributeError(f"License {tag} not found")

    def __str__(self):
        return f"{self._licenses}"
    
    def __repr__(self):
        return f"{self._licenses}"
    
    def __getitem__(self, index: int) -> ManifestLicense:
        return self._licenses[index]
    
    def __len__(self) -> int:
        return len(self._licenses)
    
    def __iter__(self) -> Generator[ManifestLicense, None, None]:
        return iter(self._licenses)
    

    # Default licenses to pick from
ManifestLicenses = ManifestLicenseList([
    ManifestLicense(tag="MIT", spdx="MIT", name="MIT License", url="https://opensource.org/licenses/MIT"),
    ManifestLicense(tag="Apache2", spdx="Apache-2.0", name="Apache License 2.0", url="https://opensource.org/licenses/Apache-2.0"),
    ManifestLicense(tag="GPL3only", spdx="GPL-3.0-only", name="GNU General Public License v3.0 only", url="https://www.gnu.org/licenses/gpl-3.0.en.html"),
    ManifestLicense(tag="BSD3Clause", spdx="BSD-3-Clause", name="BSD 3-Clause License", url="https://opensource.org/licenses/BSD-3-Clause"),
    ManifestLicense(tag="Unlicense", spdx="Unlicense", name="The Unlicense", url="https://unlicense.org/"),
    ManifestLicense(tag="CC010", spdx="CC0-1.0", name="Creative Commons Zero v1.0 Universal", url="https://creativecommons.org/publicdomain/zero/1.0/"),
    ManifestLicense(tag="Proprietary", spdx="Proprietary", name="Proprietary", url=None),
    ManifestLicense(tag="NoLicense", spdx="NoLicense", name="No License (Not Open Source)", url=None), # For explicitly stating no license / all rights reserved
])

