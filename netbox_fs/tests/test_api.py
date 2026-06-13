# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests against a real DB + real API client (no mocks).

Composes the explicit CRUD mixins (not the GraphQL-inclusive APIViewTestCase) since the plugin
ships no GraphQL type yet. Asset fixtures come from netbox-inventory (a hard dependency)."""
from dcim.models import Manufacturer
from netbox_inventory.models import Asset, InventoryItemType
from utilities.testing import APIViewTestCases
from netbox_fs.models import Disk, Filesystem, Partition


class _CRUD(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    pass


def _inv_type():
    mfr = Manufacturer.objects.create(name="ACME", slug="acme")
    return InventoryItemType.objects.create(manufacturer=mfr, model="DM1", slug="dm1")


def _assets(iit, prefix, count):
    return [
        Asset.objects.create(inventoryitem_type=iit, serial=f"{prefix}{i}", status="stored")
        for i in range(count)
    ]


class DiskAPITest(_CRUD):
    model = Disk
    brief_fields = ["asset", "display", "id", "url"]
    bulk_update_data = {"partition_scheme": "mbr"}

    @classmethod
    def setUpTestData(cls):
        iit = _inv_type()
        Disk.objects.bulk_create([Disk(asset=a, total_sectors=1_000_000) for a in _assets(iit, "DEX", 3)])
        fresh = _assets(iit, "DNEW", 3)  # asset is OneToOne -> each created Disk needs a free asset
        cls.create_data = [
            {"asset": fresh[0].pk, "total_sectors": 2_000_000, "partition_scheme": "gpt"},
            {"asset": fresh[1].pk, "total_sectors": 3_000_000, "logical_sector_size": 4096, "physical_sector_size": 4096},
            {"asset": fresh[2].pk, "total_sectors": 4_000_000, "partition_scheme": "mbr"},
        ]


class PartitionAPITest(_CRUD):
    model = Partition
    brief_fields = ["disk", "display", "id", "number", "url", "usage"]
    bulk_update_data = {"name": "bulk"}

    @classmethod
    def setUpTestData(cls):
        disk = Disk.objects.create(
            asset=Asset.objects.create(inventoryitem_type=_inv_type(), serial="PDISK", status="stored"),
            total_sectors=10_000_000,
        )
        Partition.objects.bulk_create([
            Partition(disk=disk, number=1, start_sector=2048, end_sector=100_000),
            Partition(disk=disk, number=2, start_sector=100_001, end_sector=200_000),
            Partition(disk=disk, number=3, start_sector=200_001, end_sector=300_000),
        ])
        cls.create_data = [
            {"disk": disk.pk, "number": 4, "start_sector": 300_001, "end_sector": 400_000, "usage": "zfs_member"},
            {"disk": disk.pk, "number": 5, "start_sector": 400_001, "end_sector": 500_000, "usage": "swap"},
            {"disk": disk.pk, "number": 6, "start_sector": 500_001, "end_sector": 600_000, "usage": "efi"},
        ]


class FilesystemAPITest(_CRUD):
    model = Filesystem
    brief_fields = ["display", "fs_type", "id", "partition", "url"]
    bulk_update_data = {"mountpoint": "/mnt/bulk"}

    @classmethod
    def setUpTestData(cls):
        disk = Disk.objects.create(
            asset=Asset.objects.create(inventoryitem_type=_inv_type(), serial="FSDISK", status="stored"),
            total_sectors=10_000_000,
        )
        parts = [
            Partition.objects.create(
                disk=disk, number=i + 1,
                start_sector=2048 + i * 100_000, end_sector=2048 + i * 100_000 + 50_000,
                usage="filesystem",
            )
            for i in range(6)
        ]
        Filesystem.objects.bulk_create([
            Filesystem(partition=parts[0], fs_type="ext4"),
            Filesystem(partition=parts[1], fs_type="xfs"),
            Filesystem(partition=parts[2], fs_type="swap"),
        ])
        cls.create_data = [
            {"partition": parts[3].pk, "fs_type": "ext4", "mountpoint": "/a"},
            {"partition": parts[4].pk, "fs_type": "btrfs", "label": "data"},
            {"partition": parts[5].pk, "fs_type": "vfat", "mountpoint": "/boot/efi"},
        ]
