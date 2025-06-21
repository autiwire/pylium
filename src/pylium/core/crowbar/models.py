"""
Models for dependency analysis and conflict tracking.
"""

from typing import Dict, List, Optional
from pylium.manifest import Manifest
from pydantic import BaseModel, Field


class ConflictInfo(BaseModel):
    """Information about a dependency conflict"""
    type: str  # Type of conflict (e.g. "exact_below_minimum", "multiple_exact", "no_valid_version")
    package: str  # Package name with conflict
    severity: str  # Severity level (e.g. "error", "warning")
    exact: Optional[Dict[str, str]] = None  # Details about exact version requirement
    minimum: Optional[Dict[str, str]] = None  # Details about minimum version requirement
    maximum: Optional[Dict[str, str]] = None  # Details about maximum version requirement
    versions: Optional[List[Dict[str, str]]] = None  # For multiple_exact conflicts


class DependencyStats(BaseModel):
    """Statistics about dependencies"""
    total_dependencies: int
    total_modules: int
    conflicts: int
    by_category: Dict[str, int] = Field(default_factory=dict)  # Count by category
    by_type: Dict[str, int] = Field(default_factory=dict)  # Count by type


class DependencyAnalysis(BaseModel):
    """Complete dependency analysis results"""
    dependencies: Dict[str, List[Manifest.Dependency]]
    conflicts: List[ConflictInfo]
    stats: DependencyStats

    def to_dict(self) -> dict:
        """Convert to a dictionary suitable for JSON serialization"""
        return {
            "dependencies": {
                module: [dep.model_dump() for dep in deps]
                for module, deps in self.dependencies.items()
            },
            "conflicts": [conflict.model_dump() for conflict in self.conflicts],
            "stats": self.stats.model_dump()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DependencyAnalysis":
        """Create from a dictionary (deserialization)"""
        return cls(
            dependencies={
                module: [Manifest.Dependency(**dep) for dep in deps]
                for module, deps in data["dependencies"].items()
            },
            conflicts=[ConflictInfo(**conflict) for conflict in data["conflicts"]],
            stats=DependencyStats(**data["stats"])
        ) 