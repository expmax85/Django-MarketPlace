from django.db.models import QuerySet
from stores_app.models import Seller


def add_store(user, form) -> None:
    """Create new Seller instance
    user: User model
    form: form model"""
    Seller.objects.create(owner=user, **form.cleaned_data)


def edit_store(store_slug: str, form) -> None:
    """
    Update Seller instance
    user: User model
    form: form model
    """
    Seller.objects.filter(slug=store_slug).update(**form.cleaned_data)


def get_user_stores(user) -> QuerySet:
    """
    Get queryset with all stores by user
    """
    return Seller.objects.filter(owner=user)


def get_store(slug: str) -> QuerySet:
    """
    Get store with slug
    """
    return Seller.objects.select_related('owner').get(slug=slug)
