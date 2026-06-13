# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from . import models, views

urlpatterns = [
    # Disks
    path("disks/", views.DiskListView.as_view(), name="disk_list"),
    path("disks/add/", views.DiskEditView.as_view(), name="disk_add"),
    path("disks/delete/", views.DiskBulkDeleteView.as_view(), name="disk_bulk_delete"),
    path("disks/<int:pk>/", views.DiskView.as_view(), name="disk"),
    path("disks/<int:pk>/edit/", views.DiskEditView.as_view(), name="disk_edit"),
    path("disks/<int:pk>/delete/", views.DiskDeleteView.as_view(), name="disk_delete"),
    path("disks/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="disk_changelog", kwargs={"model": models.Disk}),
    path("disks/<int:pk>/journal/", ObjectJournalView.as_view(), name="disk_journal", kwargs={"model": models.Disk}),
    # Partitions
    path("partitions/", views.PartitionListView.as_view(), name="partition_list"),
    path("partitions/add/", views.PartitionEditView.as_view(), name="partition_add"),
    path("partitions/delete/", views.PartitionBulkDeleteView.as_view(), name="partition_bulk_delete"),
    path("partitions/<int:pk>/", views.PartitionView.as_view(), name="partition"),
    path("partitions/<int:pk>/edit/", views.PartitionEditView.as_view(), name="partition_edit"),
    path("partitions/<int:pk>/delete/", views.PartitionDeleteView.as_view(), name="partition_delete"),
    path("partitions/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="partition_changelog", kwargs={"model": models.Partition}),
    path("partitions/<int:pk>/journal/", ObjectJournalView.as_view(), name="partition_journal", kwargs={"model": models.Partition}),
    # Filesystems
    path("filesystems/", views.FilesystemListView.as_view(), name="filesystem_list"),
    path("filesystems/add/", views.FilesystemEditView.as_view(), name="filesystem_add"),
    path("filesystems/delete/", views.FilesystemBulkDeleteView.as_view(), name="filesystem_bulk_delete"),
    path("filesystems/<int:pk>/", views.FilesystemView.as_view(), name="filesystem"),
    path("filesystems/<int:pk>/edit/", views.FilesystemEditView.as_view(), name="filesystem_edit"),
    path("filesystems/<int:pk>/delete/", views.FilesystemDeleteView.as_view(), name="filesystem_delete"),
    path("filesystems/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="filesystem_changelog", kwargs={"model": models.Filesystem}),
    path("filesystems/<int:pk>/journal/", ObjectJournalView.as_view(), name="filesystem_journal", kwargs={"model": models.Filesystem}),
]
