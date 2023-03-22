from typing import Optional, List, Dict, Any, Type, Union, Set
import re

import yaml

from systemrdl import RDLCompiler, RDLImporter
from systemrdl import rdltypes
from systemrdl.messages import SourceRefBase
from systemrdl import component as comp

class YAMLImporter(RDLImporter):

    def __init__(self, compiler: RDLCompiler):
        """
        Parameters
        ----------
        compiler:
            Reference to ``RDLCompiler`` instance to bind the importer to.
        """

        super().__init__(compiler)
        self.ns = None # type: str
        self._addressUnitBits = 8
        self._current_addressBlock_access = rdltypes.AccessType.rw

    @property
    def src_ref(self) -> SourceRefBase:
        return self.default_src_ref


    def import_file(self, path: str) -> None:
        """
        Import a single YAML file into the SystemRDL namespace.

        Parameters
        ----------
        path:
            Input YAML file.
        """
        super().import_file(path)

        with open(path, 'r') as file:
            file_data = yaml.safe_load(file)

        addrmap_data = self.get_addrmap(file_data)

        addrmap_def = self.decode_addrmap(addrmap_data, is_top = True)

        # Register the top definition in the root namespace
        self.register_root_component(addrmap_def)


    def get_addrmap(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        if 'addrmap' in file_data:
            addrmap_data = file_data['addrmap']
        else:
            self.msg.fatal(
                "Could not find a 'addrmap' element",
                self.src_ref
            )
        return addrmap_data


    def decode_addrmap(self, addrmap_data: Dict[str, Any], is_top: bool=False) -> comp.Addrmap:
        # validate that this reg data contains all the required fields
        if 'addr_offset' not in addrmap_data:
            self.msg.fatal("addrmap '%s' is missing 'addr_offset'" % addrmap_data['name'], self.default_src_ref)

        if is_top:
            if 'type_name' not in addrmap_data:
                self.msg.fatal("addrmap is missing 'type_name'", self.default_src_ref)
            # if this is the top node, then instantiation is skipped, and the
            # definition inherits the inst name as its type name
            addrmap_def = self.create_addrmap_definition(addrmap_data['type_name'])
        else:
            if 'inst_name' not in addrmap_data:
                self.msg.fatal("addrmap is missing 'inst_name'", self.default_src_ref)
            if 'type_name' in addrmap_data:
                # search for an existing addrmap
                addrmap_def = self.lookup_root_component(addrmap_data['type_name'])
                if addrmap_def is None:
                    self.msg.fatal("addrmap type '%s' does not exist" % addrmap_data['type_name'], self.default_src_ref)
                if not isinstance(addrmap_def, comp.Addrmap):
                    self.msg.fatal("Type '%s' is not an addrmap" % addrmap_data['type_name'], self.default_src_ref)
            else:
                # otherwise, create an anonymous definition
                addrmap_def = self.create_addrmap_definition()

        if addrmap_data.get('desc', None) is not None:
            self.assign_property(addrmap_def, 'desc', addrmap_data['desc'])

        if 'registers' in addrmap_data:
            for reg_data in addrmap_data['registers']:
                reg_inst = self.decode_reg(reg_data)
                self.add_child(addrmap_def, reg_inst)

        if 'addrmaps' in addrmap_data:
            for sub_data in addrmap_data['addrmaps']:
                sub_inst = self.decode_addrmap(sub_data, is_top = False)
                self.add_child(addrmap_def, sub_inst)

            # # Lookup the child type and call the appropriate conversion function
            # t = child_json.get('type', None)
            # if t == "addrmap":
            #     child_inst = self.decode_addrmap(child_json)
            # elif t == "regfile":
            #     child_inst = self.decode_regfile(child_json)
            # elif t == "reg":
            # else:
            #     self.msg.fatal(
            #         "Invalid child type '%s'" % t,
            #         self.default_src_ref
            #     )

            # Add the child component to this

        if is_top:
            # keep top-level addrmap as a definition. Skip instantiation
            return addrmap_def
        else:
            # For everything else, convert the definition into an instance
            inst = self.instantiate_addrmap(
                addrmap_def,
                addrmap_data['inst_name'],
                addrmap_data['addr_offset']
            )
            return inst

        # comp_def: :class:`comp.Reg`
        # inst_name: str
        # addr_offset: int
        # array_dimensions: int
        # array_stride: int

    def decode_reg(self, reg_data: Dict[str, Any]) -> comp.Reg:
        if 'inst_name' not in reg_data:
            self.msg.fatal("REG data is missing 'inst_name'", self.default_src_ref)
        if 'addr_offset' not in reg_data:
            self.msg.fatal("REG data '%s' is missing 'addr_offset'" % reg_data['inst_name'], self.default_src_ref)
        if 'fields' not in reg_data:
            self.msg.fatal("REG data is missing 'fields'", self.default_src_ref)

        reg_def = self.create_reg_definition()

        # Collect children
        for field_data in reg_data['fields']:
            # Convert each child component and add it to our reg definition
            child_inst = self.decode_field(field_data)
            self.add_child(reg_def, child_inst)

        # Convert the definition into an instance
        inst = self.instantiate_reg(
            reg_def,
            reg_data['inst_name'],
            reg_data['addr_offset'],
            reg_data.get('array_dimensions', None),
            reg_data.get('array_stride', None),
        )
        if reg_data.get('desc', None) is not None:
            self.assign_property(inst, 'desc', reg_data['desc'])
        return inst


    def decode_field(self, field_data: Dict[str, Any]) -> comp.Field:
        # validate that this field data contains all the required fields
        if 'inst_name' not in field_data:
            self.msg.fatal("FIELD data is missing 'inst_name'", self.default_src_ref)
        if 'bit_offset' not in field_data:
            self.msg.fatal("FIELD data is missing 'bit_offset'", self.default_src_ref)
        if 'bit_width' not in field_data:
            self.msg.fatal("FIELD data is missing 'bit_width'", self.default_src_ref)

        # Create an RDL field definition
        field_def = self.create_field_definition()

        # Apply reset property if it was set
        if 'reset' in field_data and field_data['reset'] is not None:
            self.assign_property(field_def, 'reset', field_data['reset'])

        # decode and apply the properties
        if 'sw' in field_data:
            type = rdltypes.AccessType[field_data['sw']]
            self.assign_property(field_def, 'sw', type)
        if 'hw' in field_data:
            type = rdltypes.AccessType[field_data['hw']]
            self.assign_property(field_def, 'hw', type)
        if 'onread' in field_data:
            type = rdltypes.OnReadType[field_data['onread']]
            self.assign_property(field_def, 'onread', type)
        if 'onwrite' in field_data:
            type = rdltypes.OnWriteType[field_data['onwrite']]
            self.assign_property(field_def, 'onwrite', type)

        # decode enum
        if 'enum' in field_data:
            enum_type_name = field_data['inst_name']+'_enum_t'
            enum_type = self.decode_enum(field_data['enum'], enum_type_name)
            self.assign_property(field_def, "encode", enum_type)


        # Instantiate the component definition
        inst = self.instantiate_field(
            field_def,
            field_data['inst_name'],
            field_data['bit_offset'],
            field_data['bit_width']
        )
        if field_data.get('desc', None) is not None:
            self.assign_property(inst, 'desc', field_data['desc'])
        return inst


    def decode_enum(self, enum_data: Dict[str, Any], type_name: str) -> Type[rdltypes.UserEnum]:
        # validate that this enum data contains all the required fields
        if 'values' not in enum_data:
            self.msg.fatal("ENUM data is missing 'values'", self.default_src_ref)

        members = []
        for value_data in enum_data['values']:
            member = self.decode_enum_value(value_data)
            members.append(member)

        enum_type = rdltypes.UserEnum.define_new(type_name, members)

        return enum_type


    def decode_enum_value(self, value_data: Dict[str, Any]) -> Type[rdltypes.UserEnumMemberContainer]:
         # validate that this value data contains all the required fields
        if 'name' not in value_data:
            self.msg.fatal("VALUE data is missing 'name'", self.default_src_ref)
        if 'value' not in value_data:
            self.msg.fatal("VALUE data is missing 'value'", self.default_src_ref)
        desc = value_data.get('desc', None)

        member = rdltypes.UserEnumMemberContainer(
            value_data['name'],
            value_data['value'],
            value_data['name'],
            desc
        )

        return member
