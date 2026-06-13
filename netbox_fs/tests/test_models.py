# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): geometry math, the overlap guard on both the
clean() path and the PostgreSQL exclusion-constraint path, uniqueness, and FK delete behaviour."""
from dcim.models import Manufacturer
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import ProtectedError
from django.db.utils import IntegrityError
from django.test import TestCase
from netbox_inventory.models import Asset, InventoryItemType
from netbox_fs.choices import FilesystemTypeChoices, PartitionUsageChoices
from netbox_fs.models import Disk, Filesystem, Partition


def _make_asset(iit, serial):
    return Asset.objects.create(inventoryitem_type=iit, serial=serial, status="stored")


class DiskModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        mfr = Manufacturer.objects.create(name="ACME", slug="acme")
        cls.iit = InventoryItemType.objects.create(manufacturer=mfr, model="DM1", slug="dm1")

    def test_create_str_url_size(self):
        disk = Disk.objects.create(
            asset=_make_asset(self.iit, "D-STR"), total_sectors=1000, logical_sector_size=512
        )
        self.assertIn("/plugins/fs/disks/", disk.get_absolute_url())
        self.assertEqual(disk.size_bytes, 512000)
        self.assertEqual(str(disk), str(disk.asset))

    def test_asset_one_to_one_and_protect(self):
        asset = _make_asset(self.iit, "D-PROT")
        Disk.objects.create(asset=asset, total_sectors=1000)
        # Deleting the underlying drive is blocked while a Disk references it.
        with self.assertRaises(ProtectedError), transaction.atomic():
            asset.delete()


class PartitionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        mfr = Manufacturer.objects.create(name="ACME", slug="acme")
        iit = InventoryItemType.objects.create(manufacturer=mfr, model="DM1", slug="dm1")
        cls.disk = Disk.objects.create(
            asset=_make_asset(iit, "P-DISK"), total_sectors=1_000_000, logical_sector_size=512
        )

    def test_inclusive_size_and_str_url(self):
        p = Partition.objects.create(
            disk=self.disk, number=1, start_sector=2048, end_sector=4095,
            usage=PartitionUsageChoices.ZFS_MEMBER,
        )
        # Inclusive LBA: 4095 - 2048 + 1 = 2048 sectors.
        self.assertEqual(p.size_sectors, 2048)
        self.assertEqual(p.size_bytes, 2048 * 512)
        self.assertIn("/plugins/fs/partitions/", p.get_absolute_url())
        self.assertEqual(str(p), f"{self.disk} #1")

    def test_unique_number_per_disk(self):
        Partition.objects.create(disk=self.disk, number=1, start_sector=2048, end_sector=4095)
        with self.assertRaises(IntegrityError), transaction.atomic():
            # Same number, non-overlapping range -> only the unique constraint should fire.
            Partition.objects.create(disk=self.disk, number=1, start_sector=4096, end_sector=8191)

    def test_clean_rejects_overlap(self):
        Partition.objects.create(disk=self.disk, number=1, start_sector=2048, end_sector=4095)
        dup = Partition(disk=self.disk, number=2, start_sector=4000, end_sector=8191)
        with self.assertRaises(ValidationError):
            dup.clean()

    def test_clean_rejects_past_end_of_disk(self):
        small = Disk.objects.create(
            asset=Asset.objects.create(
                inventoryitem_type=self.disk.asset.inventoryitem_type, serial="SMALL", status="stored"
            ),
            total_sectors=2048,
        )
        p = Partition(disk=small, number=1, start_sector=0, end_sector=5000)
        with self.assertRaises(ValidationError):
            p.clean()

    def test_clean_rejects_end_before_start(self):
        p = Partition(disk=self.disk, number=1, start_sector=8000, end_sector=4000)
        with self.assertRaises(ValidationError):
            p.clean()

    def test_db_exclusion_constraint_blocks_bulk_overlap(self):
        # bulk_create bypasses save()/clean() entirely, so this proves the DB-level guard, not clean().
        Partition.objects.create(disk=self.disk, number=1, start_sector=2048, end_sector=4095)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Partition.objects.bulk_create(
                [Partition(disk=self.disk, number=9, start_sector=4000, end_sector=8191)]
            )

    def test_adjacent_partitions_allowed(self):
        Partition.objects.create(disk=self.disk, number=1, start_sector=2048, end_sector=4095)
        # Touching but not overlapping (4096 immediately follows 4095) must be accepted.
        p2 = Partition.objects.create(disk=self.disk, number=2, start_sector=4096, end_sector=8191)
        self.assertEqual(p2.size_sectors, 4096)

    def test_dual_partition_drive(self):
        """One physical drive carrying a live member partition AND a hot-spare partition."""
        live = Partition.objects.create(
            disk=self.disk, number=1, start_sector=2048, end_sector=500_000,
            usage=PartitionUsageChoices.ZFS_MEMBER, name="live",
        )
        spare = Partition.objects.create(
            disk=self.disk, number=2, start_sector=500_001, end_sector=999_999,
            usage=PartitionUsageChoices.ZFS_MEMBER, name="spare",
        )
        self.assertEqual(self.disk.partitions.count(), 2)
        self.assertNotEqual(live.pk, spare.pk)

    def test_cascade_from_disk(self):
        p = Partition.objects.create(disk=self.disk, number=1, start_sector=2048, end_sector=4095)
        pk = p.pk
        self.disk.delete()
        self.assertFalse(Partition.objects.filter(pk=pk).exists())


class FilesystemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        mfr = Manufacturer.objects.create(name="ACME", slug="acme")
        iit = InventoryItemType.objects.create(manufacturer=mfr, model="DM1", slug="dm1")
        disk = Disk.objects.create(asset=_make_asset(iit, "FS-DISK"), total_sectors=1_000_000)
        cls.partition = Partition.objects.create(
            disk=disk, number=1, start_sector=2048, end_sector=4095,
            usage=PartitionUsageChoices.FILESYSTEM,
        )

    def test_create_str_url(self):
        fs = Filesystem.objects.create(
            partition=self.partition, fs_type=FilesystemTypeChoices.EXT4, mountpoint="/data"
        )
        self.assertIn("/plugins/fs/filesystems/", fs.get_absolute_url())
        self.assertEqual(str(fs), f"ext4 on {self.partition}")

    def test_cascade_from_partition(self):
        fs = Filesystem.objects.create(partition=self.partition, fs_type=FilesystemTypeChoices.XFS)
        pk = fs.pk
        self.partition.delete()
        self.assertFalse(Filesystem.objects.filter(pk=pk).exists())
