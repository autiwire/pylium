"""
Author type for the manifest.
"""

# Pylium imports
from .value import ManifestValue
from .version import ManifestVersion

# Built-in imports
from typing import Optional, List, Generator, Sequence

# External imports
from pydantic import Field


class ManifestAuthor(ManifestValue):
    """Author information for manifests."""
    tag: str = Field(description="Unique tag for the author")
    name: str = Field(description="Full name of the author")
    email: Optional[str] = Field(default=None, description="Email address")
    company: Optional[str] = Field(default=None, description="Company affiliation")
    since_version: Optional[ManifestVersion] = Field(default=None, description="Version when author joined")
    since_date: Optional[ManifestValue.Date] = Field(default=None, description="Date when author joined")

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
    authors: List[ManifestAuthor] = Field(default_factory=list, description="List of authors")

    @classmethod
    def create(cls, authors: Sequence[ManifestAuthor]) -> "ManifestAuthorList":
        """Create a new author list from a sequence of authors."""
        return cls(authors=list(authors))

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