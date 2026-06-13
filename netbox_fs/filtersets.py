# SPDX-License-Identifier: AGPL-3.0-or-later
import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from netbox_inventory.models import Asset
from .choices import FilesystemTypeChoices, PartitionSchemeChoices, PartitionUsageChoices
from .models import Disk, Filesystem, Partition


class DiskFilterSet(NetBoxModelFilterSet):
    # Explicit FK filter: django-filter does NOT derive `<fk>_id` from a bare FK in Meta.fields.
    asset_id = django_filters.ModelMultipleChoiceFilter(
        field_name="asset", queryset=Asset.objects.all(), label="Asset (ID)"
    )
    partition_scheme = django_filters.MultipleChoiceFilter(choices=PartitionSchemeChoices)

    class Meta:
        model = Disk
        fields = ["id", "logical_sector_size", "physical_sector_size", "total_sectors", "disk_guid"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(asset__serial__icontains=value)
            | Q(asset__name__icontains=value)
            | Q(disk_guid__icontains=value)
        )


class PartitionFilterSet(NetBoxModelFilterSet):
    disk_id = django_filters.ModelMultipleChoiceFilter(
        field_name="disk", queryset=Disk.objects.all(), label="Disk (ID)"
    )
    usage = django_filters.MultipleChoiceFilter(choices=PartitionUsageChoices)

    class Meta:
        model = Partition
        fields = ["id", "number", "name", "partition_guid", "partition_type", "start_sector", "end_sector"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(partition_guid__icontains=value)
            | Q(partition_type__icontains=value)
        )


class FilesystemFilterSet(NetBoxModelFilterSet):
    partition_id = django_filters.ModelMultipleChoiceFilter(
        field_name="partition", queryset=Partition.objects.all(), label="Partition (ID)"
    )
    fs_type = django_filters.MultipleChoiceFilter(choices=FilesystemTypeChoices)

    class Meta:
        model = Filesystem
        fields = ["id", "label", "uuid", "mountpoint"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(label__icontains=value) | Q(uuid__icontains=value) | Q(mountpoint__icontains=value)
        )
