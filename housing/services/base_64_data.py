import base64


def get_base_64_images():
    """
    Return images in base64 format
    """
    path = 'housing/samples/images/'
    paths = [
        f'{path}image1.jpg',
        f'{path}image1.jpg',
        f'{path}image1.jpg'
    ]
    base64_images = []
    for path in paths:
        with open(path, 'rb') as file:
            base64_images.append(
                base64.b64encode(file.read()),
            )
    return base64_images
