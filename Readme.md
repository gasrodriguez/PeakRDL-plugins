# Setup
## Config
Create a PeakRDL configuration file in `~/.peakrdl.toml`:
```toml
[peakrdl]

python_search_paths = [
    "<path-to-clone>/PeakRDL-plugins/src/"
]

plugins.importers.yaml = "peakrdl_yaml.__peakrdl__:Importer"
```
## Test instalation
Run this commmand:
```bash
$ peakrdl --plugins
```
Should print all available plugins:
```
importers:
        ip-xact --> peakrdl-ipxact 3.4.0
        yaml --> <path-to-clone>/PeakRDL-plugins/src/peakrdl_yaml/__peakrdl__.py:Importer
exporters:
        regblock --> peakrdl-regblock 0.11.0
        systemrdl --> peakrdl-systemrdl 0.2.0
        html --> peakrdl-html 2.10.0
        uvm --> peakrdl-uvm 2.3.0
        ip-xact --> peakrdl-ipxact 3.4.0
```
# YAML import
Go to the `examples/` directory and run this:
```bash
$ cd examples
$ peakrdl systemrdl my_subblock.yml my_block.yml -o out.rdl
```
Open the generated systemrdl file `out.rdl`. It should be equal to `my_design.rdl`.