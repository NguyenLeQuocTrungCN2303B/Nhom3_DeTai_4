from django.shortcuts import get_object_or_404
from A_Product_Mng.models import Product
def get_session_cart(request):
    """ Lấy giỏ hàng từ session nếu chưa đăng nhập """
    cart = request.session.get("cart", {})
    items = []
    total_price = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)  # Tránh lỗi 404
            quantity = item.get("quantity", 1)  # Mặc định là 1 nếu thiếu dữ liệu
            total_price_item = product.price * quantity

            items.append({
                "product": product,
                "quantity": quantity,
                "total_price": total_price_item,
                "image": item.get("image", ""),
                "detail": item.get("detail", ""),
            })

            total_price += total_price_item
        except Product.DoesNotExist:
            continue  # Nếu sản phẩm bị xóa, bỏ qua nó nhưng không crash

    order = {
        "get_cart_items": sum(item["quantity"] for item in items),
        "get_cart_total": total_price
    }

    return items, order



