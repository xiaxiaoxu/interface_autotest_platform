import redis

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
# r.set('a', 'test')
print(r.get('unique_number'))
print(r.get('a'))


