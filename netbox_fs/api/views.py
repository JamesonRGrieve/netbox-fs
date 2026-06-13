# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import Disk, Filesystem, Partition
from .serializers import DiskSerializer, FilesystemSerializer, PartitionSerializer


class DiskViewSet(NetBoxModelViewSet):
    queryset = Disk.objects.prefetch_related("asset", "tags")
    serializer_class = DiskSerializer
    filterset_class = filtersets.DiskFilterSet


class PartitionViewSet(NetBoxModelViewSet):
    queryset = Partition.objects.prefetch_related("disk", "disk__asset", "tags")
    serializer_class = PartitionSerializer
    filterset_class = filtersets.PartitionFilterSet


class FilesystemViewSet(NetBoxModelViewSet):
    queryset = Filesystem.objects.prefetch_related("partition", "partition__disk", "tags")
    serializer_class = FilesystemSerializer
    filterset_class = filtersets.FilesystemFilterSet
