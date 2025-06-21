"""
Author type for the manifest.
"""

# Pylium imports
from .value import ManifestValue

# Built-in imports
from typing import Optional, List, Generator


class ManifestAuthor(ManifestValue):
    """Author information for manifests."""
    tag: str
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    since_version: Optional[str] = None
    since_date: Optional[ManifestValue.Date] = None

    def since(self, version: str, date: ManifestValue.Date) -> "ManifestAuthor":
        """Return a copy of the author with the since version and date."""
        return ManifestAuthor(
            tag=self.tag,
            name=self.name,
            email=self.email,
            company=self.company,
            since_version=version,
            since_date=date
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, ManifestAuthor):
            return False
        return self.tag == other.tag
    
    def __hash__(self) -> int:
        return hash(self.tag)
    
    def __str__(self):
        return f"{self.name} ({self.email}) {self.company} {self.since_version} {self.since_date}"

    def __repr__(self):
        return f"{self.name} ({self.email}) {self.company} [since: {self.since_version} @ {self.since_date}]"


class ManifestAuthorList(ManifestValue):
    """List of authors with attribute-based access."""
    authors: List[ManifestAuthor]

    def __getattr__(self, tag: str) -> ManifestAuthor:        
        for author in self.authors:
            if author.tag == tag:
                return author
        raise AttributeError(f"Author {tag} not found")

    def __getitem__(self, index: int) -> ManifestAuthor:
        return self.authors[index]

    def __len__(self) -> int:
        return len(self.authors)
    
    def __iter__(self) -> Generator[ManifestAuthor, None, None]:
        return iter(self.authors)


# Type aliases for semantically different but technically same lists
ManifestMaintainerList = ManifestAuthorList
ManifestContributorList = ManifestAuthorList