# SPDX-License-Identifier: AGPL-3.0-or-later
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from netbox_inventory.models import Asset
from utilities.forms.fields import (
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField,
)
from utilities.forms.rendering import FieldSet
from .choices import FilesystemTypeChoices, PartitionSchemeChoices, PartitionUsageChoices
from .models import Disk, Filesystem, Partition


class DiskForm(NetBoxModelForm):
    asset = DynamicModelChoiceField(queryset=Asset.objects.all())

    fieldsets = (
        FieldSet("asset", "partition_scheme", "disk_guid", name="Disk"),
        FieldSet("logical_sector_size", "physical_sector_size", "total_sectors", name="Geometry"),
    )

    class Meta:
        model = Disk
        fields = [
            "asset", "logical_sector_size", "physical_sector_size", "total_sectors",
            "partition_scheme", "disk_guid", "tags",
        ]


class PartitionForm(NetBoxModelForm):
    disk = DynamicModelChoiceField(queryset=Disk.objects.all())

    fieldsets = (
        FieldSet("disk", "number", "name", "usage", name="Partition"),
        FieldSet("start_sector", "end_sector", name="Geometry (inclusive LBA)"),
        FieldSet("partition_type", "partition_guid", "attributes", name="GPT"),
    )

    class Meta:
        model = Partition
        fields = [
            "disk", "number", "name", "partition_guid", "partition_type", "start_sector",
            "end_sector", "usage", "attributes", "tags",
        ]


class FilesystemForm(NetBoxModelForm):
    partition = DynamicModelChoiceField(queryset=Partition.objects.all())

    fieldsets = (
        FieldSet("partition", "fs_type", "label", "uuid", name="Filesystem"),
        FieldSet("mountpoint", "mount_options", "advanced", name="Mount"),
    )

    class Meta:
        model = Filesystem
        fields = [
            "partition", "fs_type", "label", "uuid", "mountpoint", "mount_options", "advanced", "tags",
        ]


class DiskFilterForm(NetBoxModelFilterSetForm):
    model = Disk
    asset_id = DynamicModelMultipleChoiceField(queryset=Asset.objects.all(), required=False, label="Asset")
    partition_scheme = forms.MultipleChoiceField(choices=PartitionSchemeChoices, required=False)
    tag = TagFilterField(Disk)


class PartitionFilterForm(NetBoxModelFilterSetForm):
    model = Partition
    disk_id = DynamicModelMultipleChoiceField(queryset=Disk.objects.all(), required=False, label="Disk")
    usage = forms.MultipleChoiceField(choices=PartitionUsageChoices, required=False)
    tag = TagFilterField(Partition)


class FilesystemFilterForm(NetBoxModelFilterSetForm):
    model = Filesystem
    partition_id = DynamicModelMultipleChoiceField(queryset=Partition.objects.all(), required=False, label="Partition")
    fs_type = forms.MultipleChoiceField(choices=FilesystemTypeChoices, required=False)
    tag = TagFilterField(Filesystem)
