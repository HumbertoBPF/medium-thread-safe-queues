import threading
from collections import deque
from datetime import datetime

import matplotlib.pyplot as plt

from queues import Queue, StandardQueue, StandardConcurrentSafeQueue, OptimizedConcurrentSafeQueue


def built_in_queue():
    queue = deque([])

    queue.append(1)                             # End state of the queue = [1]
    queue.append(2)                             # End state of the queue = [1, 2]
    queue.append(3)                             # End state of the queue = [1, 2, 3]

    print("Popped item = ", queue.popleft())    # The left-most item (1) is popped

    print("Popped item = ", queue.popleft())    # The left-most item (2) is popped

    queue.append(4)

    print("Popped item = ", queue.popleft())    # The left-most item (3) is popped

def test_queue(queue: Queue):
    queue.enqueue(1)                            # End state of the queue = [1]
    queue.enqueue(2)                            # End state of the queue = [1, 2]
    queue.enqueue(3)                            # End state of the queue = [1, 2, 3]

    queue.traversal()

    print("Popped item = ", queue.dequeue())    # The left-most item (1) is popped

    queue.traversal()

    print("Popped item = ", queue.dequeue())    # The left-most item (2) is popped

    queue.traversal()
    queue.enqueue(4)

    print("Popped item = ", queue.dequeue())    # The left-most item (3) is popped

    queue.traversal()


def test_concurrent_enqueues(queue: Queue):
    # Should enqueue items from 0 to 9 to the linked list
    thread_1 = threading.Thread(target=enqueue_n_times, args=(queue, 10, 0))
    # Should enqueue items from 10 to 19 to the linked list
    thread_2 = threading.Thread(target=enqueue_n_times, args=(queue, 10, 10))

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()

    print("Traverse the queue:")
    queue.traversal()


def test_concurrent_enqueues_and_dequeues(queue: Queue):
    # Should enqueue items from 0 to 9 to the linked list
    thread_1 = threading.Thread(target=enqueue_and_dequeue_n_times, args=(queue, 10, 0))
    # Should enqueue items from 10 to 19 to the linked list
    thread_2 = threading.Thread(target=enqueue_and_dequeue_n_times, args=(queue, 10, 10))

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()

    print("Traverse the queue:")
    queue.traversal()


def enqueue_and_dequeue_n_times(queue: Queue, n: int, start_index):
    """
    Function that enqueues and dequeues into the queue n times.
    :param queue: concerned queue.
    :param n: number of insertions.
    :param start_index: starting index.
    """
    for i in range(n):
        queue.enqueue(item=start_index + i)

    for i in range(n):
        queue.dequeue()


def enqueue_n_times(queue: Queue, n: int, start_index):
    """
    Function that enqueues into the queue n times.
    :param queue: concerned queue.
    :param n: number of enqueue operations.
    :param start_index: starting index.
    """
    for i in range(n):
        queue.enqueue(item=start_index + i)


def dequeue_n_times(queue: Queue, n: int):
    """
    Function that dequeues into the queue n times.
    :param queue: concerned queue.
    :param n: number of dequeue operations.
    """
    for i in range(n):
        queue.dequeue()


def start_and_measure_threads(threads: list[threading.Thread]):
    """
    Triggers all the threads provided in the input list and measures the time until they complete.
    :param threads: an array of threading.Thread objects.
    :return: the time the threads took to complete.
    """
    initial_time = datetime.now()

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    final_time = datetime.now()
    delta_t_in_seconds = (final_time - initial_time).total_seconds()

    # Return time in milliseconds
    return delta_t_in_seconds


def spawn_threads(queue: Queue, n_threads: int) -> float:
    """
    This function spawns 2*n threads. Half of the threads perform enqueue operations and the other half perform
    dequeue operations.
    :param queue: queue to be used
    :param n_threads: number of pairs of threads to be spawned
    :return: the time it takes to complete the operations in all involved threads.
    """
    threads = []

    n_operations = 10 ** 5

    for i in range(n_threads):
        threads.append(threading.Thread(target=enqueue_n_times, args=(queue, n_operations, i)))
        threads.append(threading.Thread(target=dequeue_n_times, args=(queue, n_operations)))

    return start_and_measure_threads(threads)


def initialize_queue(queue: Queue, n: int):
    """
    Enqueues n items into the provided queue.
    :param queue: concerned queue.
    :param n: number of items to be enqueued.
    """
    for i in range(n):
        queue.enqueue(item=n)


def compare_queues():
    n_threads_array = []
    time_standard_queue_array = []
    time_standard_concurrent_safe_queue_array = []
    time_optimized_concurrent_safe_queue_array = []

    for n_threads in range(1, 9):
        standard_queue = StandardQueue()
        standard_concurrent_safe_queue = StandardConcurrentSafeQueue()
        optimized_concurrent_safe_queue = OptimizedConcurrentSafeQueue()

        t_standard_queue = spawn_threads(queue=standard_queue, n_threads=n_threads)
        t_standard_concurrent_safe_queue = spawn_threads(queue=standard_concurrent_safe_queue, n_threads=n_threads)
        t_optimized_concurrent_safe_queue = spawn_threads(queue=optimized_concurrent_safe_queue, n_threads=n_threads)

        n_threads_array.append(n_threads)
        time_standard_queue_array.append(t_standard_queue)
        time_standard_concurrent_safe_queue_array.append(t_standard_concurrent_safe_queue)
        time_optimized_concurrent_safe_queue_array.append(t_optimized_concurrent_safe_queue)

    fig, ax = plt.subplots()
    ax.plot(n_threads_array, time_standard_queue_array, color="blue", label="Standard Queue")
    ax.plot(n_threads_array, time_standard_concurrent_safe_queue_array, color="red", label="Standard Thread-Safe Queue")
    ax.plot(n_threads_array, time_optimized_concurrent_safe_queue_array, color="green", label="Optimized Thread-Safe Queue")
    ax.legend()
    ax.set_title("Comparison between multiple queue implementations")
    ax.set_xlabel("Number of threads")
    ax.set_ylabel("Time (seconds)")
    plt.show()


if __name__ == "__main__":
    compare_queues()
