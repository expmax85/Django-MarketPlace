from stores_app.models import ProductImportFile
from stores_app.forms import ImportForm

def stores_context(request):
    """
    Контекст-процессор файлов импорта
    """

    if request.user.is_authenticated:
        import_form = ImportForm()
        import_files = ProductImportFile.objects.filter(user=request.user).order_by('-created_at')
    else:
        import_form = None
        import_files = None
    return {'import_form': import_form, 'imports': import_files}