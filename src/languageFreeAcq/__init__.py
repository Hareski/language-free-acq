from importlib.metadata import version, PackageNotFoundError

from .AcqSystem import AcqSystem
from .Acquisition import Acquisition
from .Common import *
from .CspScopesRelations import CspScopesRelations
from .MaxSatAcq import MaxSatAcq
from .MaxSatOrTools import MaxSatOrTools

try:
    __version__ = version("languageFreeAcq")
except PackageNotFoundError:
    __version__ = "unknown"