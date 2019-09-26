from redis import Redis

rds = Redis(host='127.0.0.1', port=6379)


def record_add(user_id, score):
    rds.zincrby('score_order', user_id, score)


def get_begin_to_end_score(begin, end):
    score_list = rds.zrevrange('score_order', begin, end, withscores=True)
    return score_list
