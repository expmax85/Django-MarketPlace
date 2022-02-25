from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View


class AdminView(PermissionRequiredMixin, View):
    permission_required = ('profiles_app.Content_manager', )

    def get(self, request):
        return render(request, 'admin/admin_setup.html')
