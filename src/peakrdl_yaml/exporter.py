from typing import Union, Optional, TYPE_CHECKING, Any
import enum

from systemrdl.node import AddressableNode, RootNode, Node
from systemrdl.node import AddrmapNode, MemNode
from systemrdl.node import RegNode, RegfileNode, FieldNode


if TYPE_CHECKING:
    from systemrdl.messages import MessageHandler

#===============================================================================
class YAMLExporter:
    def __init__(self, **kwargs: Any) -> None:
        """
        Constructor for the exporter object.

        Parameters
        ----------
        vendor: str
            Vendor url string. Defaults to "example.org"
        library: str
            library name string. Defaults to "mylibrary"
        version: str
            Version string. Defaults to "1.0"
        standard: :class:`Standard`
            YAML Standard to use. Currently supports IEEE 1685-2009 and
            IEEE 1685-2014 (default)
        xml_indent: str
            String to use for each indent level. Defaults to 2 spaces.
        xml_newline: str
            String to use for line breaks. Defaults to a newline (``\\n``).
        """
        pass

    #---------------------------------------------------------------------------
    def export(self, node: Union[AddrmapNode, RootNode], path: str, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        node: AddrmapNode
            Top-level SystemRDL node to export.
        path:
            Path to save the exported XML file.
        """
        pass
