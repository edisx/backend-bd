from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/products/", include("api.urls.product_urls")),
    path("api/users/", include("api.urls.user_urls")),
    path("api/categories/", include("api.urls.category_urls")),
    path("api/images/", include("api.urls.image_urls")),
    path("api/models/", include("api.urls.model_urls")),
    path("api/sizes/", include("api.urls.size_urls")),
    path("api/orders/", include("api.urls.order_urls")),
    path("api/actionlogs/", include("api.urls.actionlog_urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
