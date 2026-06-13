# netbox-fs — Agent Operating Guide

Same engineering + test discipline as `../netbox-pf`, re-targeted to the **storage substrate**.

`netbox-fs` is an **AGPL-3.0** NetBox 4.6 plugin: the **native source of truth for physical disk
geometry, partitions, and filesystems**. It sits below `netbox-zfs` (which depends on it) and above
`netbox-inventory` (which owns the physical `Asset`). A drive's `Asset` stays in inventory;
`netbox-fs` adds the partition table and per-partition filesystems with **precise block geometry**.

---

## Key Directives / Rules

### DO, ALWAYS:
- If functionality won't work without a parameter, make it a **required positional** parameter —
  never an optional one with an inline presence check.
- Any time you modify a source file, ensure its accompanying test under `netbox_fs/tests/` contains
  **comprehensive tests for the change WITHOUT MOCKS**, so `manage.py test netbox_fs` discovers them.
- Write concise code (avoid obvious comments; one-liners where possible).
- **SPDX header on every source file**: `# SPDX-License-Identifier: AGPL-3.0-or-later`.

### DO NOT, EVER:
- Make assumptions, or answer with "is likely", "probably", "might be".
- Skip a failing test instead of fixing the root cause.
- **Mock the database, the ORM, the NetBox API test client, or any integration path.** Tests run
  against a **real test database**. Only pure utility functions may use mocks for isolation.

### Python / Django Guidelines:
- Import children of `datetime`: `from datetime import date` — never `import datetime` then `datetime.date`.
- Imports are package-relative inside `netbox_fs` (`from .models import Disk`).
- Models inherit `netbox.models.NetBoxModel`.
- Migrations are **hand-authored** (NetBox disables `makemigrations` in production); verify with
  `makemigrations netbox_fs --check --dry-run` on a dev/ephemeral NetBox.

---

## Architecture (NetBox 4.6 plugin)

| File | Responsibility |
|------|----------------|
| `__init__.py` | `PluginConfig` — name `netbox_fs`, `base_url='fs'`, min/max NetBox version |
| `choices.py` | `ChoiceSet`s: partition scheme, partition usage, filesystem type |
| `models.py` | `Disk`, `Partition`, `Filesystem` (see §Model) |
| `migrations/` | hand-authored schema migrations incl. the `btree_gist` overlap exclusion constraint |
| `api/` | REST API (`NetBoxModelViewSet`, `NetBoxRouter`) |
| `filtersets.py` | `NetBoxModelFilterSet` per model (explicit `<fk>_id` filters — django-filter does not derive them) |
| `tables.py`, `forms.py`, `navigation.py`, `views.py`, `urls.py`, `templates/` | UI layer |
| `graphql/` | GraphQL types (optional) |

### Model
- **`Disk`**: `asset` (OneToOne → `netbox_inventory.Asset`, **PROTECT**), `logical_sector_size`,
  `physical_sector_size`, `total_sectors` (logical sectors), `partition_scheme`, `disk_guid`.
- **`Partition`**: `disk` FK (**CASCADE**), `number`, `name`, `partition_guid`, `partition_type`,
  `start_sector`/`end_sector` (**inclusive** LBA), `usage`, `attributes` (JSON). `size_sectors`/
  `size_bytes` are **derived** properties — never stored. Overlap/fit enforced in `clean()` **and**
  a PostgreSQL exclusion constraint; `(disk, number)` is unique.
- **`Filesystem`**: `partition` (OneToOne → `Partition`, **CASCADE**), `fs_type`, `label`, `uuid`,
  `mountpoint`, `mount_options`, `advanced` (JSON). A `zfs_member` partition has no Filesystem row.

---

## Testing (NO MOCKS — real DB, NetBox test framework)

- Tests live in `netbox_fs/tests/` (one module per source module).
- Use `utilities.testing` base classes: `APIViewTestCases.*`, `create_test_device`. Build
  `netbox_inventory.Asset` (+ `InventoryItemType` + `dcim.Manufacturer`) fixtures.
- **Run**: `python /opt/netbox/app/netbox/manage.py test netbox_fs --keepdb -v2`.
- **Coverage bar**: every model, serializer, filterset, view. The partition overlap guard is tested
  on both the `clean()` path and the DB-constraint (bulk) path.

---

## Licensing
- **AGPL-3.0-or-later**. SPDX header in every file.
