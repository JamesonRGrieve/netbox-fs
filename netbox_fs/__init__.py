# SPDX-License-Identifier: AGPL-3.0-or-later
"""netbox-fs: a native NetBox source of truth for physical disk geometry, partitions, and
filesystems.

The physical drive itself lives in ``netbox-inventory`` (an ``Asset``). This plugin models the
layer below the partition table — block geometry, the precise partition map (start/end LBA, GPT
type/GUID), and per-partition filesystems — so that ``netbox-zfs`` can reference *partitions* as
vdev members. A drive may carry several partitions with different filesystems (e.g. a ZFS member
partition alongside a hot-spare partition).
"""
from netbox.plugins import PluginConfig

__version__ = "0.0.1"


class NetBoxFSConfig(PluginConfig):
    name = "netbox_fs"
    verbose_name = "Storage"
    description = "Native SoT for disk geometry, partitions, and filesystems"
    version = __version__
    author = "Jameson"
    base_url = "fs"
    min_version = "4.6.0"
    max_version = "4.6.99"


config = NetBoxFSConfig
