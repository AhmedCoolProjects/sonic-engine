import pickle
from queue import Queue
from threading import Thread
from typing import Any, Dict, Iterator, List, Union
from redis.client import PubSub
import redis

from sonic_engine.model.extension import FeatureConfig, InferenceConfig, ReportingConfig


class Database:
    "Database manager"

    def __init__(self):
        print("redis_local_con-1")
        self.redis = redis.StrictRedis(host='redis_local_con-1',
                                       port=6379,
                                       db=0,
                                       charset="utf-8",
                                       socket_keepalive=True,
                                       retry_on_timeout=True,
                                       decode_responses=False,
                                       health_check_interval=30)

        self.is_listening = False
        self.redis.flushdb()

    def register_extension(self, config: Union[FeatureConfig, InferenceConfig,
                                               ReportingConfig]) -> None:
        "Register configuration channels to the current instance"

        self.channels = config.channels
        self.pubsubs = self.subscribe_all()

    def subscribe_all(self) -> List[PubSub]:
        "Subscribe to all channels of the registered configuration if available"
        return [
            self.subscribe(ch) for ch in self.channels.subscribe
            if self.channels
        ]

    def subscribe(self, ch) -> PubSub:
        "Subscribe to channel"

        pubsub = self.redis.pubsub()
        pubsub.subscribe(ch)
        return pubsub

    def publish(self, ch, data) -> None:
        "Publish data into channel"
        self.redis.publish(ch, data)

    def get_message(self, timeout=.3) -> Iterator[Dict[str, Any]]:
        """Get messages frpm subscribed channels
        If `timeout` is specified, pass it to redis `get_message()` function
        """
        queue = Queue()

        def listen():
            while self.is_listening:
                for pubsub in self.pubsubs:
                    data = pubsub.get_message(timeout=timeout)
                    if data:
                        queue.put_nowait(data)

        self.is_listening = True
        Thread(target=listen).start()

        while True:
            if not queue.empty() and (data := queue.get_nowait()):
                data['queue_length'] = queue.qsize()
                yield data

    def stop_listening(self):
        'Stop listening to redis channels'
        self.is_listening = False

    def store(self, name, key, data):
        "Store in the database using `hset`"
        return self.redis.hset(name, key, pickle.dumps(data))

    def retrieve(self, name, key):
        "Retrieve from the database using `hget`"
        data = self.redis.hget(name, key)
        return pickle.loads(data)

    def delete(self, name, key):
        "Delete from the database using `hdel`"
        return self.redis.hdel(name, key)


__db__ = Database()
