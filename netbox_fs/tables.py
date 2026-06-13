# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import Disk, Filesystem, Partition


class DiskTable(NetBoxTable):
    asset = tables.Column(linkify=True)
    partition_scheme = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_fs:disk_list")

    class Meta(NetBoxTable.Meta):
        model = Disk
        fields = (
            "pk", "id", "asset", "logical_sector_size", "physical_sector_size", "total_sectors",
            "partition_scheme", "disk_guid", "tags", "created", "last_updated",
        )
        default_columns = ("asset", "partition_scheme", "logical_sector_size", "total_sectors")


class PartitionTable(NetBoxTable):
    disk = tables.Column(linkify=True)
    usage = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_fs:partition_list")

    class Meta(NetBoxTable.Meta):
        model = Partition
        fields = (
            "pk", "id", "disk", "number", "name", "usage", "partition_type", "partition_guid",
            "start_sector", "end_sector", "tags", "created", "last_updated",
        )
        default_columns = ("disk", "number", "name", "usage", "start_sector", "end_sector")


class FilesystemTable(NetBoxTable):
    partition = tables.Column(linkify=True)
    fs_type = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_fs:filesystem_list")

    class Meta(NetBoxTable.Meta):
        model = Filesystem
        fields = (
            "pk", "id", "partition", "fs_type", "label", "uuid", "mountpoint", "mount_options",
            "tags", "created", "last_updated",
        )
        default_columns = ("partition", "fs_type", "label", "mountpoint")
