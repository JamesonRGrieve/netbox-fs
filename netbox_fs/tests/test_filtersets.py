# SPDX-License-Identifier: AGPL-3.0-or-later
"""FilterSet tests against a real DB (no mocks): the explicit `<fk>_id` filters scope correctly."""
from dcim.models import Manufacturer
from django.test import TestCase
from netbox_inventory.models import Asset, InventoryItemType
from netbox_fs.choices import FilesystemTypeChoices, PartitionUsageChoices
from netbox_fs.filtersets import DiskFilterSet, FilesystemFilterSet, PartitionFilterSet
from netbox_fs.models import Disk, Filesystem, Partition


def _inv_type():
    mfr = Manufacturer.objects.create(name="ACME", slug="acme")
    return InventoryItemType.objects.create(manufacturer=mfr, model="DM1", slug="dm1")


class DiskFilterSetTest(TestCase):
    queryset = Disk.objects.all()

    @classmethod
    def setUpTestData(cls):
        iit = _inv_type()
        cls.a1 = Asset.objects.create(inventoryitem_type=iit, serial="AAA111", status="stored")
        cls.a2 = Asset.objects.create(inventoryitem_type=iit, serial="BBB222", status="stored")
        Disk.objects.create(asset=cls.a1, total_sectors=1000, partition_scheme="gpt", disk_guid="GUID-1")
        Disk.objects.create(asset=cls.a2, total_sectors=2000, partition_scheme="mbr", disk_guid="GUID-2")

    def test_asset_id(self):
        self.assertEqual(DiskFilterSet({"asset_id": [self.a1.pk]}, self.queryset).qs.count(), 1)

    def test_partition_scheme(self):
        self.assertEqual(DiskFilterSet({"partition_scheme": ["gpt"]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(DiskFilterSet({"q": "AAA111"}, self.queryset).qs.count(), 1)
        self.assertEqual(DiskFilterSet({"q": "GUID-2"}, self.queryset).qs.count(), 1)


class PartitionFilterSetTest(TestCase):
    queryset = Partition.objects.all()

    @classmethod
    def setUpTestData(cls):
        iit = _inv_type()
        cls.disk = Disk.objects.create(
            asset=Asset.objects.create(inventoryitem_type=iit, serial="PD1", status="stored"),
            total_sectors=10_000_000,
        )
        cls.disk2 = Disk.objects.create(
            asset=Asset.objects.create(inventoryitem_type=iit, serial="PD2", status="stored"),
            total_sectors=10_000_000,
        )
        Partition.objects.create(disk=cls.disk, number=1, start_sector=2048, end_sector=100_000,
                                 usage=PartitionUsageChoices.ZFS_MEMBER, name="live")
        Partition.objects.create(disk=cls.disk, number=2, start_sector=100_001, end_sector=200_000,
                                 usage=PartitionUsageChoices.SWAP, name="swp")
        Partition.objects.create(disk=cls.disk2, number=1, start_sector=2048, end_sector=100_000,
                                 usage=PartitionUsageChoices.EFI, name="esp")

    def test_disk_id(self):
        self.assertEqual(self.queryset.count(), 3)
        self.assertEqual(PartitionFilterSet({"disk_id": [self.disk.pk]}, self.queryset).qs.count(), 2)
        self.assertEqual(PartitionFilterSet({"disk_id": [self.disk2.pk]}, self.queryset).qs.count(), 1)

    def test_usage(self):
        self.assertEqual(PartitionFilterSet({"usage": [PartitionUsageChoices.ZFS_MEMBER]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(PartitionFilterSet({"q": "live"}, self.queryset).qs.count(), 1)


class FilesystemFilterSetTest(TestCase):
    queryset = Filesystem.objects.all()

    @classmethod
    def setUpTestData(cls):
        iit = _inv_type()
        disk = Disk.objects.create(
            asset=Asset.objects.create(inventoryitem_type=iit, serial="FD1", status="stored"),
            total_sectors=10_000_000,
        )
        parts = [
            Partition.objects.create(disk=disk, number=i + 1, start_sector=2048 + i * 100_000,
                                     end_sector=2048 + i * 100_000 + 50_000, usage="filesystem")
            for i in range(3)
        ]
        cls.fs1 = Filesystem.objects.create(partition=parts[0], fs_type=FilesystemTypeChoices.EXT4,
                                            label="root", mountpoint="/")
        Filesystem.objects.create(partition=parts[1], fs_type=FilesystemTypeChoices.XFS, mountpoint="/data")
        Filesystem.objects.create(partition=parts[2], fs_type=FilesystemTypeChoices.SWAP)

    def test_partition_id(self):
        self.assertEqual(FilesystemFilterSet({"partition_id": [self.fs1.partition_id]}, self.queryset).qs.count(), 1)

    def test_fs_type(self):
        self.assertEqual(FilesystemFilterSet({"fs_type": [FilesystemTypeChoices.EXT4]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(FilesystemFilterSet({"q": "root"}, self.queryset).qs.count(), 1)
        self.assertEqual(FilesystemFilterSet({"q": "/data"}, self.queryset).qs.count(), 1)
