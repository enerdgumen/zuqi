from environs import Env

env = Env()
env.read_env()

with env.prefixed("CONDUCTOR_"):
    port = env.int('PORT')
    log_level = env('LOG_LEVEL')
