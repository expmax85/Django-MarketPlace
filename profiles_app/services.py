from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


def get_user_and_change_password(email):
    user = User.objects.filter(email=email).first()
    if user:
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()
        return user
    return False


def get_auth_user(form):
    email = form.cleaned_data['email']
    raw_password = form.cleaned_data['password1']
    return authenticate(email=email, password=raw_password)
