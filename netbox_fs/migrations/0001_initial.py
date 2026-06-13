# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored initial migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_fs --check --dry-run   (on a dev/ephemeral NetBox)
#
# The final RunSQL adds a PostgreSQL EXCLUDE constraint so two partitions on the same disk can
# never have overlapping inclusive sector ranges — race-free and bulk/API/migration-proof, unlike
# the model clean() which only guards the interactive path. It needs the `btree_gist` extension
# (bundled with postgresql-contrib); the migrating DB user must be able to CREATE EXTENSION.
import django.core.validators
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
        # Asset is created in netbox-inventory's FIRST migration; __first__ is name-agnostic
        # (this lab's is 0001_initial_prod; upstream is 0001_initial — a hard pin breaks one or the other).
        ("netbox_inventory", "__first__"),
    ]
    operations = [
        migrations.CreateModel(
            name="Disk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("logical_sector_size", models.PositiveIntegerField(default=512, validators=[django.core.validators.MinValueValidator(1)])),
                ("physical_sector_size", models.PositiveIntegerField(default=4096, validators=[django.core.validators.MinValueValidator(1)])),
                ("total_sectors", models.BigIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("partition_scheme", models.CharField(default="gpt", max_length=16)),
                ("disk_guid", models.CharField(blank=True, max_length=64)),
                ("asset", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="disk", to="netbox_inventory.asset")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={"verbose_name": "Disk", "ordering": ["asset"]},
        ),
        migrations.CreateModel(
            name="Partition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("number", models.PositiveSmallIntegerField()),
                ("name", models.CharField(blank=True, max_length=128)),
                ("partition_guid", models.CharField(blank=True, max_length=64)),
                ("partition_type", models.CharField(blank=True, max_length=64)),
                ("start_sector", models.BigIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ("end_sector", models.BigIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ("usage", models.CharField(default="unknown", max_length=16)),
                ("attributes", models.JSONField(blank=True, default=dict)),
                ("disk", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="partitions", to="netbox_fs.disk")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "Partition",
                "ordering": ["disk", "number"],
                "constraints": [models.UniqueConstraint(fields=("disk", "number"), name="netbox_fs_partition_unique_disk_number")],
            },
        ),
        migrations.CreateModel(
            name="Filesystem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("fs_type", models.CharField(max_length=16)),
                ("label", models.CharField(blank=True, max_length=128)),
                ("uuid", models.CharField(blank=True, max_length=64)),
                ("mountpoint", models.CharField(blank=True, max_length=255)),
                ("mount_options", models.CharField(blank=True, max_length=255)),
                ("advanced", models.JSONField(blank=True, default=dict)),
                ("partition", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="filesystem", to="netbox_fs.partition")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={"verbose_name": "Filesystem", "ordering": ["partition"]},
        ),
        migrations.RunSQL(
            sql=[
                "CREATE EXTENSION IF NOT EXISTS btree_gist;",
                "ALTER TABLE netbox_fs_partition ADD CONSTRAINT netbox_fs_partition_no_overlap "
                "EXCLUDE USING gist (disk_id WITH =, int8range(start_sector, end_sector, '[]') WITH &&);",
            ],
            reverse_sql=[
                "ALTER TABLE netbox_fs_partition DROP CONSTRAINT IF EXISTS netbox_fs_partition_no_overlap;",
            ],
        ),
    ]
