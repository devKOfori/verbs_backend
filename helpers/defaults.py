from django.apps import apps

ORDER_QTY_DEFAULT = 1

ORDER_DISCOUNT_DEFAULT = 0.00

PRODUCT_QTY_DEFAULT = 1

TOKEN_EXPIRY_HOURS = 10

ITEM_TAX_DEFAULT = 0

RESET_PASSWORD_STATUS_DEFAULT = "new"

def default_payment_status():
    OrderPaymentStatus = apps.get_model("api", "OrderPaymentStatus")
    default_payment_status, _ = OrderPaymentStatus.objects.get_or_create("Default Status")
    return default_payment_status

def product_grade_default():
    ProductGrade = apps.get_model('api', 'ProductGrade')
    default_grade, _ = ProductGrade.objects.get_or_create(name="Default Grade")
    return default_grade.id

def product_type_default():
    ProductType = apps.get_model('api', 'ProductType')
    default_type, _ = ProductType.objects.get_or_create(name="Default Type")
    return default_type.id

def product_color_default():
    ProductColor = apps.get_model('api', 'Color')
    default_color, _ = ProductColor.objects.get_or_create(name="Default Color")
    return default_color.id

def product_frame_type_default():
    FrameType = apps.get_model('api', 'FrameType')
    default_frame_type, _ = FrameType.objects.get_or_create(name="Wood")
    return default_frame_type.id

def order_status_default():
    OrderStatus = apps.get_model("api", "OrderStatus")
    default_order_status, _ = OrderStatus.objects.get_or_create(name="In Queue")
    return default_order_status.id

def order_payment_status_default():
    OrderPaymentStatus = apps.get_model("api", "OrderPaymentStatus")
    default_order_payment_status, _ = OrderPaymentStatus.objects.get_or_create(name="Default Status")
    return default_order_payment_status.id