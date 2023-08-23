import sys
import redis


if __name__ == '__main__':
    count = 0
    for i in range(16):
        redis_client = redis.Redis(host='localhost', port=6379, db=i)
        num_tasks = redis_client.llen('task_queue')
        count += num_tasks
        for t in range(num_tasks):
            task = redis_client.lpop('task_queue')
print(f'Finished Clean, clean {count} elements')
            