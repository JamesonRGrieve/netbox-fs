<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-fs

A NetBox 4.6 plugin: a **native source of truth for physical disk geometry, partitions, and
filesystems**. It is the storage-layer foundation that `netbox-zfs` builds on.

`netbox-inventory` already models the *physical drive* as an `Asset` (serial, capacity, SMART,
media). `netbox-fs` adds the layer below the partition table:

- **Disk** — block geometry for one drive: logical/physical sector size, total sectors, partition
  scheme (GPT/MBR). 1:1 with a `netbox_inventory.Asset` (the drive itself stays in inventory).
- **Partition** — a precise region of a disk: `start_sector`/`end_sector` (inclusive LBA), derived
  block count, GPT type/GUID, attribute flags, and a `usage` marker (`filesystem`, `zfs_member`,
  `swap`, `efi`, `bios_boot`, `raw`, …). A drive can hold many partitions — e.g. one ZFS
  vdev-member partition **and** a separate hot-spare partition.
- **Filesystem** — the formatted filesystem on a partition (ext4/xfs/swap/vfat/…): label, UUID,
  mountpoint, mount options, plus per-fs-type params in `advanced` (JSON). A `zfs_member` partition
  has **no** Filesystem row — ZFS consumes it raw (see `netbox-zfs`).

## Why a separate plugin

ZFS pools reference partitions, not whole drives, and not every partition is ZFS. Modeling disks,
partitions, and non-ZFS filesystems here keeps the storage substrate reusable and lets `netbox-zfs`
depend on it without dragging ZFS concepts into generic partitioning.

## Integrity guarantees

- A partition must fit within its disk and **must not overlap** a sibling. Enforced twice: a model
  `clean()` for friendly form errors, and a PostgreSQL `EXCLUDE USING gist` constraint
  (`btree_gist`) that is race-free and survives bulk/API/migration writes.
- Partition numbers are unique per disk.
- Deleting an `Asset` is **blocked** (`PROTECT`) while a `Disk` references it; deleting a `Disk`
  cascades to its partitions and their filesystems.

## Model

```
netbox_inventory.Asset  (physical drive)
        ▲ OneToOne (PROTECT)
      Disk  ── sector sizes, total_sectors, scheme, disk_guid
        ▲ FK (CASCADE)
   Partition ── number, start/end LBA (inclusive), usage, partition_type/guid, attributes
        ▲ OneToOne (CASCADE)
  Filesystem ── fs_type, label, uuid, mountpoint, mount_options, advanced
```

All models inherit `NetBoxModel` (custom fields, tags, change logging, GraphQL, REST API).

## Install

Requires PostgreSQL with the `btree_gist` extension (bundled with `postgresql-contrib`; the
initial migration runs `CREATE EXTENSION IF NOT EXISTS btree_gist`).

```bash
uv pip install --python /opt/netbox/venv/bin/python -e .   # editable; or: pip install netbox-fs
# add "netbox_fs" to PLUGINS in configuration.py (before netbox_zfs)
python manage.py migrate netbox_fs
python manage.py collectstatic --no-input
systemctl restart netbox netbox-rq
```

## Develop / test

Tests run against a **real NetBox test database** (no mocks). They build
`netbox_inventory.Asset` fixtures, so `netbox-inventory` must be installed.

```bash
python /opt/netbox/app/netbox/manage.py test netbox_fs --keepdb -v2
# verify the hand-authored migration matches the models (on a dev/ephemeral NetBox):
python /opt/netbox/app/netbox/manage.py makemigrations netbox_fs --check --dry-run
```

## License

AGPL-3.0-or-later.
