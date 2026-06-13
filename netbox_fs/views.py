# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.views import generic
from . import filtersets, forms, models, tables


class DiskView(generic.ObjectView):
    queryset = models.Disk.objects.all()


class DiskListView(generic.ObjectListView):
    queryset = models.Disk.objects.all()
    table = tables.DiskTable
    filterset = filtersets.DiskFilterSet
    filterset_form = forms.DiskFilterForm


class DiskEditView(generic.ObjectEditView):
    queryset = models.Disk.objects.all()
    form = forms.DiskForm


class DiskDeleteView(generic.ObjectDeleteView):
    queryset = models.Disk.objects.all()


class DiskBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Disk.objects.all()
    table = tables.DiskTable


class PartitionView(generic.ObjectView):
    queryset = models.Partition.objects.all()


class PartitionListView(generic.ObjectListView):
    queryset = models.Partition.objects.all()
    table = tables.PartitionTable
    filterset = filtersets.PartitionFilterSet
    filterset_form = forms.PartitionFilterForm


class PartitionEditView(generic.ObjectEditView):
    queryset = models.Partition.objects.all()
    form = forms.PartitionForm


class PartitionDeleteView(generic.ObjectDeleteView):
    queryset = models.Partition.objects.all()


class PartitionBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Partition.objects.all()
    table = tables.PartitionTable


class FilesystemView(generic.ObjectView):
    queryset = models.Filesystem.objects.all()


class FilesystemListView(generic.ObjectListView):
    queryset = models.Filesystem.objects.all()
    table = tables.FilesystemTable
    filterset = filtersets.FilesystemFilterSet
    filterset_form = forms.FilesystemFilterForm


class FilesystemEditView(generic.ObjectEditView):
    queryset = models.Filesystem.objects.all()
    form = forms.FilesystemForm


class FilesystemDeleteView(generic.ObjectDeleteView):
    queryset = models.Filesystem.objects.all()


class FilesystemBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Filesystem.objects.all()
    table = tables.FilesystemTable
