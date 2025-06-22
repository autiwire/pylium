"""
Backend type for the manifest.
"""

# Standard library imports
from enum import Flag
from typing import Any

# External imports
from pydantic import computed_field


class ManifestBackendGroup(Flag):
    NoBackendGroup = 0
    Database = 1 << 0
    File = 1 << 1
    Network = 1 << 2
    Container = 1 << 3
    All = Database | File | Network | Container

    def __str__(self):
        # If the flag instance has a specific name (it's a single defined flag or a named combination like 'All')
        if self.name is not None:
            return self.name.lower()
        else:
            # It's an unnamed combination (e.g., Database | File) or a value like 0 if not directly named.
            decomposed_members = list(self)
            
            if not decomposed_members:
                # This implies self.value is 0.
                if self.value == 0:
                    for member_in_class in self.__class__:
                        if member_in_class.value == 0:
                            return member_in_class.name.lower() # e.g., "nobackendgroup"
                    return "0" 
                else:
                    return str(self.value) 

            return " | ".join(m.name.lower() for m in decomposed_members)
    
    def __repr__(self):
        cls_name = self.__class__.__name__
        decomposed_members = list(self)

        if not decomposed_members:
            if self.value == 0:
                for member_in_class in self.__class__:
                    if member_in_class.value == 0:
                        return f"{cls_name}.{member_in_class.name}" 
                return f"<{cls_name}: 0>" 
            else:
                return f"<{cls_name} value: {self.value}>"

        member_reprs = [f"{cls_name}.{m.name}" for m in decomposed_members]
        return " | ".join(member_reprs)
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestBackendGroup):
            return False
        return self.value == other.value


class ManifestBackend(Flag):
    NoBackend       = 0
    SQLite          = 1 << 0
    Redis           = 1 << 1
    PostgreSQL      = 1 << 2
    File            = 1 << 3
    MQTT            = 1 << 4
    Docker          = 1 << 5
    All             = SQLite | Redis | PostgreSQL | File | MQTT | Docker

    @computed_field
    @property
    def group(self) -> "ManifestBackendGroup":
        """Get the backend group(s) this backend belongs to."""
        mapping = {
            ManifestBackend.SQLite: ManifestBackendGroup.Database,
            ManifestBackend.Redis: ManifestBackendGroup.Database | ManifestBackendGroup.Network,
            ManifestBackend.PostgreSQL: ManifestBackendGroup.Database | ManifestBackendGroup.Network,
            ManifestBackend.File: ManifestBackendGroup.File,
            ManifestBackend.MQTT: ManifestBackendGroup.Network,
            ManifestBackend.Docker: ManifestBackendGroup.Container | ManifestBackendGroup.Network,
        }

        result = ManifestBackendGroup.NoBackendGroup
        for member in self.__class__:
            if self & member:
                result |= mapping.get(member, ManifestBackendGroup.NoBackendGroup)
        return result

    def __str__(self):
        base_str_val = ""
        # If the flag instance has a specific name (it's a single defined flag or a named combination like 'All')
        if self.name is not None:
            base_str_val = self.name.lower()
        else:
            # It's an unnamed combination (e.g., SQLite | Redis) or a value like 0 if not directly named.
            decomposed_members = list(self)
            
            if not decomposed_members:
                # This implies self.value is 0.
                if self.value == 0:
                    # Try to find a name for the zero value among defined members.
                    for member_in_class in self.__class__:
                        if member_in_class.value == 0: 
                            base_str_val = member_in_class.name.lower()
                            break 
                    else: 
                        base_str_val = "0" 
                else:
                    base_str_val = str(self.value) 
            else:
                base_str_val = " | ".join(m.name.lower() for m in decomposed_members)
        
        group_str = str(self.group).replace(" | ", ", ")
        return f"{base_str_val} (group: {group_str})"
    
    def __repr__(self):
        cls_name = self.__class__.__name__
        base_repr_val = ""
        decomposed_members = list(self)

        if not decomposed_members:
            # This typically means self.value == 0.
            if self.value == 0:
                # Try to find a named zero member for a canonical representation
                for member_in_class in self.__class__:
                    if member_in_class.value == 0: # name will exist for defined members
                        base_repr_val = f"{cls_name}.{member_in_class.name}"
                        break
                else: # no break
                    base_repr_val = f"<{cls_name}: 0>" 
            else:
                # Should not happen for Flags if list(self) is empty and value isn't 0
                base_repr_val = f"<{cls_name} value: {self.value}>"
        else:
            member_reprs = [f"{cls_name}.{m.name}" for m in decomposed_members]
            base_repr_val = " | ".join(member_reprs)
        
        group_repr = repr(self.group) # Calculate group repr
        return f"{base_repr_val} (group: {group_repr})"
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestBackend):
            return False
        return self.value == other.value