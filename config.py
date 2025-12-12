import secrets

secret_key = secrets.token_hex(16)
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
max_image_size = 2 * 1024 * 1024  # 2 MB
