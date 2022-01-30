from collections import deque
from math import ceil
import sys


class Node:
    def __init__(self, i, w):
        self.index = i
        self.word = w
        self.visited = False
        self.distance = 100000
        self.next_node = None
        self.len = len(w)
        self.half = int(ceil(self.len/2))


def main():
    #get words to join
    try:
        str_start = sys.argv[1]
        str_end = sys.argv[2]
    except IndexError:
        print("please give two words to join in args")
        sys.exit(1)

    dictionary = []
    nodes = []

    #put search words at the start to make the search slightly faster
    dictionary.append(str_start)
    dictionary.append(str_end)

    #read in dictionary
    for line in sys.stdin :
        dictionary.append(line.rstrip())

    #check if any values were read in
    if len(dictionary) == 2 :
        print("please pass a dictionary to stdin")
        sys.exit(1)

    #remove duplicates
    dictionary = list(dict.fromkeys(dictionary))
    dictionary.sort()

    #use dictionary to create a node for each word
    for i, word in enumerate(dictionary) :
        nodes.append(Node(i, word))

    #finding where the start and end words are in the nodes list
    start = nodes[dictionary.index(str_start)]
    end = nodes[dictionary.index(str_end)]

    print(start.word, end.word)

    #search for links in singled and double joined mode and print results
    if (str_start == str_end):
        print("1", str_start, str_end)
        print("1", str_start, str_end)
    else:
        single_len = bfs(nodes, True)
        print(*single_len)
        double_len = bfs(nodes, False)
        print(*double_len)


    sys.exit(0)


def bfs(nodes, single):
    start = nodes[0]
    end = nodes[1]

    #visit the start node
    start.distance = 1
    start.visited = True

    #queue the starting node and start the search
    queue = deque([start])
    #while stack still has items
    while(queue):
        node = queue.popleft()
        if single:
            neighbours = find_neighbours_single(nodes, node)
        else:
            neighbours = find_neighbours_double(nodes, node)


        for node in neighbours:
            #check if we reached the end word
            if(node == end):
                #create a list of words joining start and end to return
                out = [node.distance, node.word]
                while not node.next_node == None:
                    node = node.next_node
                    out.insert(1, node.word)

                reset_graph(nodes)
                return out
            
            queue.append(node)
            # print("queued", node.word)

    reset_graph(nodes)
    #didn't find a link
    return[0]


def reset_graph(graph):
    for node in graph:
        node.visited = False
        node.distance = 100000
        node.next_node = None


def find_neighbours_single(nodes, left):
    lw = left.word
    # minimum length of the matching part of the left word
    suffix_len = left.half

    neighbours = []

    for right in nodes:
        if(right.visited):
            continue

        rw = right.word

        # check how big the matching string must be
        preffix_len = right.half
        match_len = min(suffix_len, preffix_len)
        for check_len in range(match_len, min(len(lw), len(rw))+1):
            # check if suffix matches prefix of next word
            if(lw[-check_len:] == rw[0:check_len]):
                # visit node
                right.next_node = left
                right.distance = left.distance + 1
                right.visited = True
                # save the neighbour to the return list
                neighbours.append(right)
            # else: print("rejected", right.word)

    return neighbours


def find_neighbours_double(nodes, left):
    lw = left.word
    # minimum length of the matching part of the left word
    suffix_len = left.half

    neighbours = []

    for right in nodes:
        if(right.visited):
            continue

        rw = right.word

        # check how big the matching string must be
        preffix_len = right.half
        match_len = max(suffix_len, preffix_len)
        for check_len in range(match_len, min(len(lw), len(rw))+1):
            # check if suffix matches prefix of next word
            if(lw[-check_len:] == rw[0:check_len]):
                # visit node
                right.next_node = left
                right.distance = left.distance + 1
                right.visited = True
                # save the neighbour to the return list
                neighbours.append(right)
            # else: print("rejected", right.word)

    return neighbours



if __name__ == "__main__":
    main()