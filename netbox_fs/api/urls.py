# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.routers import NetBoxRouter
from . import views

app_name = "netbox_fs"

router = NetBoxRouter()
router.register("disks", views.DiskViewSet)
router.register("partitions", views.PartitionViewSet)
router.register("filesystems", views.FilesystemViewSet)

urlpatterns = router.urls
