from django.urls import path, include

app_name = 'v2'

urlpatterns = [
    path("", include("gps.agency_v2.gps.urls")),
    path("brand/", include("gps.agency_v2.brand.urls")),
    path("report/", include("gps.agency_v2.report.urls")),
]
