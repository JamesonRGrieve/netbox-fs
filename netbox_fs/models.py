# SPDX-License-Identifier: AGPL-3.0-or-later
"""Storage substrate model: a disk's block geometry, its partition map, and per-partition
filesystems. Block counts are precise (inclusive LBA), and partitions cannot overlap."""
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from .choices import FilesystemTypeChoices, PartitionSchemeChoices, PartitionUsageChoices


class Disk(NetBoxModel):
    """Block geometry for one physical drive, 1:1 with the ``netbox-inventory`` Asset that owns the
    drive's identity (serial, capacity, SMART). This model adds only what partitioning needs."""

    asset = models.OneToOneField(
        "netbox_inventory.Asset",
        on_delete=models.PROTECT,
        related_name="disk",
        help_text="The physical drive (netbox-inventory Asset) this geometry describes.",
    )
    logical_sector_size = models.PositiveIntegerField(
        default=512,
        validators=[MinValueValidator(1)],
        help_text="Addressable sector size in bytes (the LBA unit; partition sectors count these). Usually 512 or 4096.",
    )
    physical_sector_size = models.PositiveIntegerField(
        default=4096,
        validators=[MinValueValidator(1)],
        help_text="Hardware sector size in bytes; drives partition alignment. 512e drives are 512 logical / 4096 physical.",
    )
    total_sectors = models.BigIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total addressable capacity of the disk, in logical sectors.",
    )
    partition_scheme = models.CharField(
        max_length=16, choices=PartitionSchemeChoices, default=PartitionSchemeChoices.GPT
    )
    disk_guid = models.CharField(max_length=64, blank=True, help_text="GPT disk GUID.")

    class Meta:
        ordering = ["asset"]
        verbose_name = "Disk"

    def __str__(self):
        return str(self.asset)

    def get_absolute_url(self):
        return reverse("plugins:netbox_fs:disk", args=[self.pk])

    @property
    def size_bytes(self):
        return self.total_sectors * self.logical_sector_size


class Partition(NetBoxModel):
    """A precise region of a disk. ``start_sector`` and ``end_sector`` are **inclusive** LBAs (the
    GPT first-LBA/last-LBA convention), so ``size_sectors = end - start + 1``. Size is always
    derived — never stored — so it can't drift from the boundaries."""

    disk = models.ForeignKey(Disk, on_delete=models.CASCADE, related_name="partitions")
    number = models.PositiveSmallIntegerField(help_text="Partition number within the table (1-based).")
    name = models.CharField(max_length=128, blank=True, help_text="GPT partition name / label.")
    partition_guid = models.CharField(
        max_length=64, blank=True, help_text="GPT unique partition GUID (PARTUUID)."
    )
    partition_type = models.CharField(
        max_length=64,
        blank=True,
        help_text="GPT partition-type GUID or MBR type code (e.g. BF01 = Solaris/ZFS, EF00 = EFI).",
    )
    start_sector = models.BigIntegerField(
        validators=[MinValueValidator(0)],
        help_text="First LBA (inclusive), counted in the disk's logical sectors.",
    )
    end_sector = models.BigIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Last LBA (inclusive), counted in the disk's logical sectors.",
    )
    usage = models.CharField(
        max_length=16, choices=PartitionUsageChoices, default=PartitionUsageChoices.UNKNOWN
    )
    attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text="GPT attribute bits & flags (required, legacy_bios_bootable, read_only, no_automount, …).",
    )

    class Meta:
        ordering = ["disk", "number"]
        verbose_name = "Partition"
        constraints = [
            models.UniqueConstraint(
                fields=["disk", "number"], name="netbox_fs_partition_unique_disk_number"
            ),
        ]

    def __str__(self):
        return f"{self.disk} #{self.number}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_fs:partition", args=[self.pk])

    @property
    def size_sectors(self):
        if self.start_sector is None or self.end_sector is None:
            return None
        return self.end_sector - self.start_sector + 1

    @property
    def size_bytes(self):
        sectors = self.size_sectors
        if sectors is None:
            return None
        return sectors * self.disk.logical_sector_size

    def clean(self):
        super().clean()
        if self.start_sector is None or self.end_sector is None:
            return
        errors = {}
        if self.end_sector < self.start_sector:
            errors["end_sector"] = "end_sector must be greater than or equal to start_sector."
        if self.disk_id:
            if self.end_sector > self.disk.total_sectors - 1:
                errors["end_sector"] = (
                    f"Partition extends past the disk: last LBA is {self.disk.total_sectors - 1}."
                )
            if not errors:
                # Single-query overlap test using the inclusive-range predicate
                # (a.start <= b.end AND a.end >= b.start); no per-row loop.
                overlap = (
                    Partition.objects.filter(disk_id=self.disk_id)
                    .exclude(pk=self.pk)
                    .filter(start_sector__lte=self.end_sector, end_sector__gte=self.start_sector)
                )
                if overlap.exists():
                    errors["start_sector"] = "Partition range overlaps another partition on this disk."
        if errors:
            raise ValidationError(errors)


class Filesystem(NetBoxModel):
    """The formatted filesystem on a partition. A ``zfs_member`` partition has no Filesystem row —
    ZFS consumes the partition raw; its pool/dataset structure lives in ``netbox-zfs``."""

    partition = models.OneToOneField(
        Partition, on_delete=models.CASCADE, related_name="filesystem"
    )
    fs_type = models.CharField(max_length=16, choices=FilesystemTypeChoices)
    label = models.CharField(max_length=128, blank=True)
    uuid = models.CharField(max_length=64, blank=True, help_text="Filesystem UUID (blkid UUID).")
    mountpoint = models.CharField(max_length=255, blank=True)
    mount_options = models.CharField(
        max_length=255, blank=True, help_text="fstab-style options, comma-separated."
    )
    advanced = models.JSONField(
        default=dict,
        blank=True,
        help_text="Per-fs-type parameters (ext4 block size & reserved-blocks-pct, xfs su/sw, …).",
    )

    class Meta:
        ordering = ["partition"]
        verbose_name = "Filesystem"

    def __str__(self):
        return f"{self.get_fs_type_display()} on {self.partition}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_fs:filesystem", args=[self.pk])
