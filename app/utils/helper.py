def serialize_product(product):
    return {
        "id": product.id,
        "name": product.name,
        "image": product.image,
        "telegram_file_id": product.telegram_file_id,
        "price": product.price,
        "discount": product.discount
    }
