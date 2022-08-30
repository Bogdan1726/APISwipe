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
    for i in range(len(paths)):
        with open(paths[i], 'rb') as file:
            base64_images.append(
                {
                    'order': i + 1,
                    'image': base64.b64encode(file.read()),

                }
            )
    return base64_images
