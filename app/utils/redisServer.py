from redis import Redis

rds = Redis(host='127.0.0.1', port=6379)

# redis添加打卡数据，用户id加上score分数，若原先没有key，则新建一个初始值为0
def record_add(user_id, score):
    rds.zincrby('score_order', user_id, score)

# 获取排名从begin到end排名分数信息
def get_begin_to_end_score(begin, end):
    score_list = rds.zrevrange('score_order', begin, end, withscores=True)
    return score_list

# 通过user获得排名
def get_order_by_user(user_id):
    rank = rds.zrevrank(name='score_order', value=user_id)
    return rank