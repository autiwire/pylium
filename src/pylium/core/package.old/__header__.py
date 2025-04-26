"""
This file is the header file for pylium packages.
It is used to define the package and its components.

"""

from ._pylium import _Pylium

from abc import ABC
from typing import Optional
import sys
import os
import importlib
import inspect
from enum import Enum

class Package(_Pylium, metaclass=_Pylium.Meta):
    """
    A class that represents a package.

    Inherit this class into the main class of the package in the header file.

    """

    def __init__(self):
        print(f"Package init: {self}")
        super().__init__()

    def __new__(cls, *args, **kwargs):
        print(f"Package new: {cls}")
        # First try to get custom implementation
        pass

    @classmethod
    def _find_implementation(cls):
        # Get the module name from the class name
        module_name = cls.__module__
        print(f"Module name: {module_name}")
        # Get the implementation file
        implementation_file = f"{module_name}.py"
        print(f"Implementation file: {implementation_file}")
    
    def test(self):
        # Get the metaclass using type()
        metaclass = type(self)
        print(f"Metaclass: {metaclass}")
        # Or using __class__
        print(f"Metaclass (via __class__): {self.__class__.__class__}")
        raise NotImplementedError("Package test - header")

