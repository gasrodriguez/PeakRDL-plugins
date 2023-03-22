from typing import TYPE_CHECKING
import re

from peakrdl.plugins.importer import ImporterPlugin #pylint: disable=import-error
from peakrdl.plugins.exporter import ExporterSubcommandPlugin #pylint: disable=import-error

from .exporter import YAMLExporter
from .importer import YAMLImporter

if TYPE_CHECKING:
    import argparse
    from systemrdl import RDLCompiler
    from systemrdl.node import AddrmapNode


class Exporter(ExporterSubcommandPlugin):
    short_desc = "Export the register model to YAML"


    def add_exporter_arguments(self, arg_group: 'argparse.ArgumentParser') -> None:
       return None


    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:

        x = YAMLExporter()
        x.export(
            top_node,
            options.output,
            component_name=options.name
        )


class Importer(ImporterPlugin):
    file_extensions = ["yml", "yaml"]

    def add_importer_arguments(self, arg_group: 'argparse.ArgumentParser') -> None:
        return None

    def do_import(self, rdlc: 'RDLCompiler', options: 'argparse.Namespace', path: str) -> None:
        i = YAMLImporter(rdlc)
        i.import_file(
            path
        )
