from django.contrib.auth import get_user_model


User = get_user_model()


def get_user_and_change_password(email):
    user = User.objects.filter(email=email).first()
    if user:
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()
        return user
    return False
