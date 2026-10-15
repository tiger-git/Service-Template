# ================================ JWT ================================
JWT_SECRET_KEY = "MVzKDkorbkf_rXahutekyaqpf5rJUIkrV7bni0owC7U"
ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 15
REFRESH_EXPIRE_DAYS = 1

# ================================ redis key =================================
REDIS_KEY_REFRESH_TOKENS = "REFRESH_TOKEN:{token}"