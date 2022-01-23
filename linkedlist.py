
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None

class CLinkedList:
    def __init__(self):
        self.head = None
    def append(self, val):
        newnode = Node(val)
        if self.head is None:
            newnode.next = newnode
            self.head = newnode
        else:
            prev = self.head
            while(prev.next != self.head):
                prev = prev.next
            prev.next = newnode
            newnode.next = self.head
            self.head = newnode
    def next(self):
        self.head=self.head.next
        return self.head
    def printlist(self):
        if self.head is None:
            print("List is empty")
            return
        current = self.head.next

        print("List: \n"+self.head.val)
        while(current != self.head):
            print(current.val)
            current=current.next
        return
