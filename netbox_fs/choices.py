# SPDX-License-Identifier: AGPL-3.0-or-later
"""Choice sets for the storage model. Values match the tokens reported by `lsblk`/`blkid`/`sgdisk`."""
from utilities.choices import ChoiceSet


class PartitionSchemeChoices(ChoiceSet):
    """The partition table format on a disk."""

    GPT = "gpt"
    MBR = "mbr"
    NONE = "none"
    UNKNOWN = "unknown"
    CHOICES = [
        (GPT, "GPT"),
        (MBR, "MBR (MS-DOS)"),
        (NONE, "Unpartitioned"),
        (UNKNOWN, "Unknown"),
    ]


class PartitionUsageChoices(ChoiceSet):
    """What a partition is used for. ``zfs_member`` partitions are consumed raw by ZFS and carry
    no ``Filesystem`` row — they are referenced by ``netbox-zfs`` vdev members instead."""

    FILESYSTEM = "filesystem"
    ZFS_MEMBER = "zfs_member"
    SWAP = "swap"
    EFI = "efi"
    BIOS_BOOT = "bios_boot"
    LVM_PV = "lvm_pv"
    MD_MEMBER = "md_member"
    RAW = "raw"
    UNKNOWN = "unknown"
    CHOICES = [
        (FILESYSTEM, "Filesystem", "blue"),
        (ZFS_MEMBER, "ZFS member", "indigo"),
        (SWAP, "Swap", "orange"),
        (EFI, "EFI system", "green"),
        (BIOS_BOOT, "BIOS boot", "gray"),
        (LVM_PV, "LVM physical volume", "purple"),
        (MD_MEMBER, "Linux RAID member", "purple"),
        (RAW, "Raw / unformatted", "gray"),
        (UNKNOWN, "Unknown", "gray"),
    ]


class FilesystemTypeChoices(ChoiceSet):
    """Mountable filesystem types (the ``blkid TYPE=`` token)."""

    EXT2 = "ext2"
    EXT3 = "ext3"
    EXT4 = "ext4"
    XFS = "xfs"
    BTRFS = "btrfs"
    F2FS = "f2fs"
    SWAP = "swap"
    VFAT = "vfat"
    EXFAT = "exfat"
    NTFS = "ntfs"
    ISO9660 = "iso9660"
    OTHER = "other"
    CHOICES = [
        (EXT2, "ext2"),
        (EXT3, "ext3"),
        (EXT4, "ext4"),
        (XFS, "XFS"),
        (BTRFS, "Btrfs"),
        (F2FS, "F2FS"),
        (SWAP, "swap"),
        (VFAT, "FAT/VFAT"),
        (EXFAT, "exFAT"),
        (NTFS, "NTFS"),
        (ISO9660, "ISO 9660"),
        (OTHER, "Other"),
    ]
