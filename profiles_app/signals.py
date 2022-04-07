from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed

User = get_user_model()


def user_group_changed_handler(sender, action, **kwargs) -> None:
    """
    Signal for adding is_staff for user in content-manager
    """
    instance = kwargs['instance']
    model = kwargs['model']
    queryset = model.objects.filter(id__in=list(kwargs['pk_set']))
    if isinstance(instance, User):
        model_list = [item.name for item in queryset]
        if 'Content-manager' in model_list and not instance.is_superuser:
            if action == 'pre_add':
                instance.is_staff = True
            if action == 'pre_remove':
                instance.is_staff = False
            instance.save(update_fields=['is_staff'])
    elif isinstance(instance, Group):
        if instance.name == 'Content-manager':
            model_list = list(queryset)
            for item in model_list:
                if not item.is_superuser:
                    if action == 'pre_add':
                        item.is_staff = True
                    if action == 'pre_remove':
                        item.is_staff = False
            model.objects.bulk_update(model_list, ['is_staff'])


m2m_changed.connect(user_group_changed_handler, sender=User.groups.through)
