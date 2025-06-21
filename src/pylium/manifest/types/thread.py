"""
Thread safety type for the manifest.
"""

# Standard library imports
from enum import Enum
from typing import Any

# External imports
from pydantic import computed_field

class ManifestThreadSafety(Enum):
    Unsafe     = "unsafe"
    Reentrant  = "reentrant"
    ThreadSafe = "thread-safe"
    ActorSafe  = "actor-safe"
    Immutable  = "immutable"

    def __str__(self):
        return f"{self.name.lower()}"

    def __repr__(self):
        return f"{self.name.lower()}"

    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestThreadSafety):
            return False
        return self.value == other.value
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    @computed_field
    @property
    def description(self) -> str:
        """Get the description of the thread safety level."""
        return {
            ManifestThreadSafety.Unsafe: "No synchronization, may cause race conditions.",
            ManifestThreadSafety.Reentrant: "Reentrant for single thread recursion, not parallel-safe.",
            ManifestThreadSafety.ThreadSafe: "Internally synchronized for parallel access.",
            ManifestThreadSafety.ActorSafe: "Thread-safe via actor/queue-based serialized access.",
            ManifestThreadSafety.Immutable: "Immutable after creation, safe by design."
        }[self]