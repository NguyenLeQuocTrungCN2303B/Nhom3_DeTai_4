from django import template

register = template.Library()

@register.filter
def intcomma_custom(value):
    try:
        value = int(value)  # Chuyển sang số nguyên để loại bỏ phần thập phân
        value = (value // 1000) * 1000  # Làm tròn 3 số cuối thành 000
        return "{:,}".format(value).replace(",", ".")  # Định dạng số với dấu "."
    except (ValueError, TypeError):
        return value  # Nếu lỗi, trả về nguyên bản
