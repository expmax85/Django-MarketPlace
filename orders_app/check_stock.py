from stores_app.models import SellerProduct


def check_stock(product: SellerProduct, delta: int) -> bool:
    """ Проверка наличия на складе """
    if product.quantity >= delta:
        product.quantity -= delta
        product.save()
        return True
    return False
