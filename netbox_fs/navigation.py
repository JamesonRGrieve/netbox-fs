# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

_disks = PluginMenuItem(
    link="plugins:netbox_fs:disk_list",
    link_text="Disks",
    buttons=[PluginMenuButton("plugins:netbox_fs:disk_add", "Add", "mdi mdi-plus-thick")],
)
_partitions = PluginMenuItem(
    link="plugins:netbox_fs:partition_list",
    link_text="Partitions",
    buttons=[PluginMenuButton("plugins:netbox_fs:partition_add", "Add", "mdi mdi-plus-thick")],
)
_filesystems = PluginMenuItem(
    link="plugins:netbox_fs:filesystem_list",
    link_text="Filesystems",
    buttons=[PluginMenuButton("plugins:netbox_fs:filesystem_add", "Add", "mdi mdi-plus-thick")],
)

menu = PluginMenu(
    label="Storage / Filesystems",
    groups=(("Storage", (_disks, _partitions, _filesystems)),),
    icon_class="mdi mdi-harddisk",
)
