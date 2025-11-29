import threading
import time
from abc import ABC, abstractmethod
from typing import Optional


class Node:
    def __init__(self, key: int):
        self.key: int = key
        self.next: Optional[Node] = None

    def __str__(self):
        return str(self.key)


class Queue(ABC):
    def __init__(self):
        self._head: Optional[Node] = None
        self._tail: Optional[Node] = self._head

    @abstractmethod
    def enqueue(self, item: int):
        """
        Adds the provided integer item to the queue.
        :param item: value to be added to the queue.
        """
        pass

    @abstractmethod
    def dequeue(self) -> Optional[int]:
        """
        Drops an item from the queue.
        :return: the dropped item.
        """
        pass

    def traversal(self):
        """
        Iterates over all the item in the queue. While doing so, the items are printed.
        """
        current_node = self._head

        while current_node is not None:
            print(current_node.key, end=" -> ")
            current_node = current_node.next

        print("")


class StandardQueue(Queue):
    def enqueue(self, item: int):
        new_node = Node(key=item)

        # If the queue is empty, we must set the head
        if self._head is None:
            self._head = new_node

        # If the queue is not empty, we have to add the new node to the end of it
        # We do so by making the tail point to it
        if self._tail is not None:
            self._tail.next = new_node

        # Delay to force race condition to happen
        # time.sleep(0.1)

        # Update the tail by making it point to the new node
        self._tail = new_node


    def dequeue(self) -> Optional[int]:
        # Item to be returned
        old_head = self._head

        if old_head is not None:
            # Update the head to the item that comes right after it
            new_head = old_head.next
            self._head = new_head

            # Delay to force race condition to happen
            # time.sleep(0.1)

            # Detach the head from the linked list since it will be returned
            old_head.next = None

            # If the underlying linked list becomes empty, we have to update the tail
            if new_head is None:
                self._tail = new_head

        return old_head


class StandardConcurrentSafeQueue(StandardQueue):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

    def enqueue(self, item: int):
        self.lock.acquire()
        super().enqueue(item=item)
        self.lock.release()

    def dequeue(self) -> Optional[int]:
        self.lock.acquire()
        dropped_item = super().dequeue()
        self.lock.release()
        return dropped_item


class OptimizedConcurrentSafeQueue(StandardQueue):
    def __init__(self):
        super().__init__()
        # This node is used to decouple the head from the tail
        dummy_node = Node(key=0)
        self._head = dummy_node
        self._tail = self._head
        self.head_lock = threading.Lock()
        self.tail_lock = threading.Lock()

    def enqueue(self, item: int):
        self.tail_lock.acquire()
        new_node = Node(key=item)

        # If the queue is not empty, we have to add the new node to the end of it
        # We do so by making the tail point to it
        if self._tail is not None:
            self._tail.next = new_node

        # Delay to force race condition to happen
        # time.sleep(0.1)

        # Update the tail by making it point to the new node
        self._tail = new_node
        self.tail_lock.release()

    def dequeue(self) -> Optional[int]:
        self.head_lock.acquire()
        # The first item is always the dummy node
        dummy_node = self._head

        # The second item is the item that will be actually dropped
        dropped_node = dummy_node.next

        # If only the dummy node is in the list return immediately
        if dropped_node is None:
            self.head_lock.release()
            return None

        # Replace the dummy node since we are dropping one item
        self._head = dropped_node

        # Delay to force race condition to happen
        # time.sleep(0.1)

        # Detach the head from the linked list since it will be returned
        dummy_node.next = None

        self.head_lock.release()
        return dropped_node.key

    def traversal(self):
        """
        Iterates over all the item in the queue. While doing so, the items are printed.
        """
        dummy_node = self._head
        # The dummy node must be skipped since it is a virtual node intended to decouple the head from the tail
        current_node = dummy_node.next

        while current_node is not None:
            print(current_node.key, end=" -> ")
            current_node = current_node.next

        print("")
