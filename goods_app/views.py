from django.shortcuts import render
from banners_app.services import banner


def index(request):
    banners = banner()

    return render(request, 'index.html', {'banners': banners})
