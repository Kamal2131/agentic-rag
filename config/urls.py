from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.rag.health import health_check, readiness_check

urlpatterns = [
    path("admin/", admin.site.urls),
    # Health checks
    path("health/", health_check, name="health"),
    path("ready/", readiness_check, name="readiness"),
    # API
    path("api/rag/", include("apps.rag.urls")),
    path("api/knowledgebase/", include("apps.knowledgebase.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
