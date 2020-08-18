import datetime
from typing import List
from dataclasses import dataclass
from lxml import etree
from .user_classes import Owner, Permission
from .port_classes import PortList

from .utils import (
    get_bool_from_element,
    get_int_from_element,
    get_text_from_element,
    get_datetime_from_element,
)


@dataclass
class Scanner:
    """
    Arguments:
        uuid: uuid of the scanner.
        owner: Owner of the scanner.
        comment: The comment on the scanner.
        creation_time: Date and time the scanner was created.
        modification_time: Date an time the scanner was last modified.
        writable: Whether the scanner is writable.
        in_use: Whether the scanner is in use.
        permissions: Permissions that the current user has on the scanner.
        port: Port of the scanner.
        scanner_type: Type of the scanner.
        trash: Whether the scanner is in the trashcan.
        all_info_loaded: Whether all informatione is loaded.
    """

    uuid: str = None
    owner: Owner = None
    name: str = None
    comment: str = None
    creation_time: datetime.datetime = None
    modification_time: datetime.datetime = None
    writable: bool = None
    in_use: bool = None
    permissions: list = None
    # hosts
    port: int = None
    scanner_type: int = None
    # ca_pub
    # credential
    trash: bool = None
    all_info_loaded: bool = False

    @staticmethod
    def resolve_scanners(root: etree.Element) -> list:
        """ Resolve information of a 'scanners' element from GMP.

        Arguments:
            root: scanners XML-Element from GMP.
        """
        scanners = []

        for child in root:
            if child.tag == "scanner":
                scanners.append(Scanner.resolve_scanner(child))

        if len(scanners) == 1:
            return scanners[0]
        else:
            return scanners

    @staticmethod
    def resolve_scanner(root: etree.Element) -> "Scanner":
        if root is None:
            return None
        uuid = root.get("id")
        owner = Owner.resolve_owner(root.find("owner"))
        name = root.find("name").text
        comment = get_text_from_element(root, "comment")

        creation_time = get_datetime_from_element(root, "creation_time")
        modification_time = get_datetime_from_element(root, "modification_time")

        writable = get_bool_from_element(root, "writable")
        in_use = get_bool_from_element(root, "in_use")

        permissions = Permission.resolve_permissions(root.find("permissions"))
        # host
        port = get_int_from_element(root, "port")
        scanner_type = get_int_from_element(root, "type")

        trash = get_bool_from_element(root, "trash")

        scanner = Scanner(
            uuid,
            owner,
            name,
            comment,
            creation_time,
            modification_time,
            writable,
            in_use,
            permissions,
            # host,
            port,
            scanner_type,
            trash,
            False,
        )
        return scanner


@dataclass
class Target:
    gmp: "Gmp" = None
    uuid: str = None
    owner: Owner = None
    name: str = None
    comment: str = None
    creation_time: datetime.datetime = None
    modification_time: datetime.datetime = None
    writable: bool = None
    in_use: bool = None
    permissions: list = None
    hosts: List[str] = None
    exclude_hosts: List[str] = None
    # ssh_credential
    # smb_credential
    # esxi_credential
    # snmp_credential
    reverse_lookup_only: bool = None
    reverse_lookup_unify: bool = None
    # alive_tests: str ?
    trash: bool = None
    all_info_loaded: bool = None
    _port_list: PortList = None

    @staticmethod
    def resolve_targets(root: etree.Element, gmp) -> list:
        targets = []
        for child in root:
            if child.tag == "target":
                targets.append(Target.resolve_target(child, gmp))

        if len(targets) == 1:
            return targets[0]
        else:
            return targets

    @staticmethod
    def resolve_target(root: etree.Element, gmp) -> "Target":
        if root is None:
            return None
        uuid = root.get("id")
        owner = Owner.resolve_owner(root.find("owner"))
        name = root.find("name").text
        comment = get_text_from_element(root, "comment")

        creation_time = get_datetime_from_element(root, "creation_time")
        modification_time = get_datetime_from_element(root, "modification_time")

        writable = get_bool_from_element(root, "writable")
        in_use = get_bool_from_element(root, "in_use")

        permissions = Permission.resolve_permissions(root.find("permissions"))
        hosts = get_text_from_element(root, "hosts")
        if hosts is not None:
            hosts = hosts.replace(" ", "")
            hosts = hosts.split(",")

        exclude_hosts = get_text_from_element(root, "exclude_hosts")
        if exclude_hosts is not None:
            exclude_hosts = exclude_hosts.replace(" ", "")
            exclude_hosts = exclude_hosts.split(",")

        port_list = PortList.resolve_port_list(root.find("port_list"))
        # ssh_credential
        # smb_credential
        # esxi_credential
        # snmp_credential

        reverse_lookup_only = get_bool_from_element(root, "reverse_lookup_only")
        reverse_lookup_unify = get_bool_from_element(
            root, "reverse_lookup_unify"
        )

        # alive_tests: str ?
        trash = get_bool_from_element(root, "trash")

        return Target(
            gmp,
            uuid,
            owner,
            name,
            comment,
            creation_time,
            modification_time,
            writable,
            in_use,
            permissions,
            hosts,
            exclude_hosts,
            # ssh_credential,
            # smb_credential,
            # esxi_credential,
            # snmp_credential,
            reverse_lookup_only,
            reverse_lookup_unify,
            trash,
            False,
            port_list,
        )

    def load_port_list(self, gmp):
        self._port_list = gmp.get_port_list(self._port_list.uuid).port_lists

    @property
    def port_list(self) -> PortList:
        self.load_port_list(self.gmp)
        return self._port_list

    @port_list.setter
    def port_list(self, port_list: PortList):
        self._port_list = port_list
