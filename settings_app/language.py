from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import translate_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import check_for_language


def set_language(request):
    """
    Redirect to a given URL while setting the chosen language in the session
    (if enabled) and in a cookie. The URL and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    print(f'********start')
    print(f'********  {request.POST["LANGUAGE_QUERY_PARAMETER"]}')

    next_url = request.POST.get('next', request.GET.get('next'))
    if (
        (next_url or request.accepts('text/html')) and
        not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
    ):
        next_url = request.META.get('HTTP_REFERER')
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = '/'
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)
    if request.method == 'POST':
        lang_code = request.POST['LANGUAGE_QUERY_PARAMETER']
        if lang_code and check_for_language(lang_code):
            if next_url:
                next_trans = translate_url(next_url, lang_code)
                if next_trans != next_url:
                    response = HttpResponseRedirect(next_trans)
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME, lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
    return response