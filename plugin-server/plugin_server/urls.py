from django.contrib import admin
from django.urls import path

from api.router import api
from api.mcp import mcp_sse, mcp_messages

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("mcp/", mcp_sse, name="mcp-sse"),
    path("mcp/messages/", mcp_messages, name="mcp-messages"),
]
