from django.urls import path, include

urlpatterns = [
    path('', include('ticket.admin_v2.ticket.urls')),
    path('latency/', include('ticket.admin_v2.latency.urls')),
    path('report/', include('ticket.admin_v2.report.urls')),
]
