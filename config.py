import secrets

SECRET_KEY = secrets.token_hex(16)
CSRF_TOKEN_KEY = secrets.token_hex(16)
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB
