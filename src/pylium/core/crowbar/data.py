"""
Data classes for serializable dependency information.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from pylium.manifest import Manifest

from pydantic import BaseModel, Field, field_serializer


class DependencyInfo(BaseModel):
    """Serializable dependency information"""
    name: str
    version: str
    direction: str  # One of: MINIMUM, EXACT, MAXIMUM
    type: str  # One of: PIP, PYLIUM
    category: Optional[str] = None  # One of: BUILD, RUNTIME, AUTOMATIC, DEVELOPMENT
    source: Optional[str] = None  # Source URL if applicable

    @classmethod
    def from_manifest_dependency(cls, dep: Manifest.Dependency) -> "DependencyInfo":
        """Create from a Manifest.Dependency instance"""
        return cls(
            name=dep.name,
            version=dep.version,
            direction=dep.direction.name if hasattr(dep, 'direction') else 'MINIMUM',
            type=dep.type.name if hasattr(dep, 'type') else 'PIP',
            category=dep.category.name if hasattr(dep, 'category') else None,
            source=dep.source
        )

    def to_manifest_dependency(self) -> Manifest.Dependency:
        """Convert to a Manifest.Dependency instance"""
        return Manifest.Dependency(
            name=self.name,
            version=self.version,
            type=getattr(Manifest.DependencyType, self.type),
            direction=getattr(Manifest.DependencyDirection, self.direction),
            category=getattr(Manifest.DependencyCategory, self.category) if self.category else None,
            source=self.source
        )


class ConflictInfo(BaseModel):
    """Information about a dependency conflict"""
    type: str  # Type of conflict (e.g. "exact_below_minimum")
    package: str  # Package name with conflict
    severity: str  # Severity level (e.g. "error", "warning")
    exact: Dict[str, str]  # Details about exact version requirement
    minimum: Dict[str, str]  # Details about minimum version requirement


class DependencyStats(BaseModel):
    """Statistics about dependencies"""
    total_dependencies: int
    total_modules: int
    conflicts: int
    by_category: Dict[str, int] = Field(default_factory=dict)  # Count by category
    by_type: Dict[str, int] = Field(default_factory=dict)  # Count by type


class DependencyAnalysis(BaseModel):
    """Complete dependency analysis results"""
    dependencies: Dict[str, List[DependencyInfo]]
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
                module: [DependencyInfo(**dep) for dep in deps]
                for module, deps in data["dependencies"].items()
            },
            conflicts=[ConflictInfo(**conflict) for conflict in data["conflicts"]],
            stats=DependencyStats(**data["stats"])
        ) 