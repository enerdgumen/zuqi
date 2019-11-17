from environs import Env

env = Env()
env.read_env()

with env.prefixed("CONDUCTOR_"):
    port = env.int('PORT')
    log_level = env('LOG_LEVEL')
    challenge_timeout_seconds = env.int('CHALLENGE_TIMEOUT_SECONDS')
    static_files_path = env('STATIC_FILES_PATH')
    trivia_max_fetch_tentatives = env.int('TRIVIA_MAX_FETCH_TENTATIVES')
    trivia_fetch_size = env.int('TRIVIA_FETCH_SIZE')