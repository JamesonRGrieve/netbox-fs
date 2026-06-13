# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from ..models import Disk, Filesystem, Partition


class DiskSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_fs-api:disk-detail")
    # `asset` is left as the default PK-related field rather than nesting netbox-inventory's
    # AssetSerializer — that keeps this plugin's API decoupled from inventory's serializer internals.
    size_bytes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Disk
        fields = [
            "id", "url", "display", "asset", "logical_sector_size", "physical_sector_size",
            "total_sectors", "size_bytes", "partition_scheme", "disk_guid",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "asset"]


class PartitionSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_fs-api:partition-detail")
    disk = DiskSerializer(nested=True)
    size_sectors = serializers.IntegerField(read_only=True)
    size_bytes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Partition
        fields = [
            "id", "url", "display", "disk", "number", "name", "partition_guid", "partition_type",
            "start_sector", "end_sector", "size_sectors", "size_bytes", "usage", "attributes",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "disk", "number", "usage"]


class FilesystemSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_fs-api:filesystem-detail")
    partition = PartitionSerializer(nested=True)

    class Meta:
        model = Filesystem
        fields = [
            "id", "url", "display", "partition", "fs_type", "label", "uuid", "mountpoint",
            "mount_options", "advanced", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "partition", "fs_type"]
