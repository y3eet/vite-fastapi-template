from argon2 import PasswordHasher, Type

ph = PasswordHasher(
    time_cost=3,  # number of iterations
    memory_cost=65536,  # memory usage in KiB (64 MB here)
    parallelism=4,  # number of threads
    hash_len=32,  # length of the hash in bytes
    salt_len=16,  # length of random salt in bytes
    type=Type.ID,  # Argon2id (recommended variant)
)
