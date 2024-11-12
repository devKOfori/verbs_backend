def product_image_storage_path(instance, file_name):
    return f"{instance.product.id}/{file_name}"