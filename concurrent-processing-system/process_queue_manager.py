import multiprocessing as mp
import random
import time
from datetime import datetime


def producer(producer_id, queue, semaphore):
    while True:
        semaphore.acquire()
        items = [random.randint(1, 100) for _ in range(3)]
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Producer {producer_id} produced items: {items}")
        queue.put((producer_id, items))
        semaphore.release()
        time.sleep(random.uniform(1, 3))


def consumer(consumer_id, queue, semaphore):
    while True:
        semaphore.acquire()
        try:
            producer_id, items = queue.get()
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Consumer {consumer_id} consumed items from Producer {producer_id}: {items}")
            time.sleep(random.uniform(0.5, 1.5))
        finally:
            semaphore.release()


if __name__ == "__main__":
    NUM_PRODUCERS = 3
    NUM_CONSUMERS = 3
    MAX_PRODUCTION = 5
    MAX_CONSUMPTION = 2
    
    queue = mp.Queue(MAX_PRODUCTION)
    producer_semaphore = mp.Semaphore(MAX_PRODUCTION)
    consumer_semaphore = mp.Semaphore(MAX_CONSUMPTION)

    producers = [
        mp.Process(target=producer, args=(i, queue, producer_semaphore))
        for i in range(NUM_PRODUCERS)
    ]
    for p in producers:
        p.start()

    consumers = [
        mp.Process(target=consumer, args=(i, queue, consumer_semaphore))
        for i in range(NUM_CONSUMERS)
    ]
    for c in consumers:
        c.start()

    try:
        for p in producers:
            p.join()
        for c in consumers:
            c.join()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        for p in producers:
            p.terminate()
        for c in consumers:
            c.terminate()