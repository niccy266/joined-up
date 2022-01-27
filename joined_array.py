from collections import deque
from math import ceil
import numpy as np
from functools import wraps
import sys
import queue
from bisect import bisect


def memoize(function):
    memo = {}
    @wraps(function)
    def wrapper(*args):
        try:
            return memo[args]
        except KeyError:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


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
    global halves_a
    #get words to join
    try:
        str_start = sys.argv[1]
        str_end = sys.argv[2]
    except IndexError:
        print("please give two words to join in args")
        sys.exit(1)

    dictionary = []
    nodes = []


    #read in dictionary
    for line in sys.stdin :
        dictionary.append(line.rstrip().lower())

    #check if any values were read in
    if len(dictionary) == 0 :
        print("please pass a dictionary to stdin")
        sys.exit(1)

    dictionary.append(str_start)
    dictionary.append(str_end)

    #put search words at the start to make the search slightly faster
    #dictionary.insert(0, str_start)
    #dictionary.insert(1, str_end)

    dictionary.sort()
    #remove duplicates
    dictionary = list(dict.fromkeys(dictionary))

    #use dictionary to create a node for each word
    for i, word in enumerate(dictionary) :
        nodes.append(Node(i, word))

    halves = []
    for node in nodes :
        halves.append(node.half)
    halves_a = np.array(halves, dtype=int)

    print(str_start, str_end)
    #search for links in singled and double joined mode and print results
    if (str_start == str_end):
        print("1", str_start, str_end)
        print("1", str_start, str_end)
    else:
        start = dictionary.index(str_start)
        end = dictionary.index(str_end)
        
        single_len = bfs(dictionary, halves, True, start, end)
        print(*single_len)
        double_len = bfs(dictionary, halves, False, start, end)
        print(*double_len)

    sys.exit(0)


def bfs(dictionary, halves, single, start_i, end_i):

    end = dictionary[end_i]

    visited = np.array([False] * len(dictionary), dtype=bool)
    distance = np.array([100000] * len(dictionary), dtype=int)

    #visit the start node
    distance[start_i] = 1
    visited[start_i] = True

    #hashmap = dict.fromkeys(dictionary)
    a_map = np.array([-1] * len(dictionary), dtype=int)

    #queue the starting node and start the search
    q = queue.Queue(len(dictionary))
    #print("Initialising the queue with starting word", dictionary[start_i])
    q.put(start_i)
    #while stack still has items
    while(not q.empty()):
        l = q.get()

        if single:
            neighbours = find_neighbours_single(dictionary, visited, distance, halves, a_map, l)
        else:
            neighbours = find_neighbours_double(dictionary, visited, distance, halves, a_map, l)
        
        for i in neighbours:
            if(i == end_i):
                print(distance)
                print(a_map)
                r = i
                #create a list of words joining start and end to return
                out = [distance[r], dictionary[r]]
                while(a_map[r]!= -1):
                    r = a_map[r]
                    out.insert(1, dictionary[r])

                return out
            
            q.put(i)
            visited[i] = True

    #didn't find a chain
    return[0]


def find_neighbours_single(dictionary, visited, distance, halves, a_map, l):
    lw = dictionary[l]
    #minimum length of the matching part of the left word
    suffix_len = halves[l]

    neighbours = np.zeros(len(dictionary), dtype=int)
    count = 0


    for match_len in range(1, len(lw)):
        #print("matching strings of length", match_len)
        #print("matching strings of length", match_len)
        left = bisect(dictionary, lw[-match_len:])
        right = bisect(dictionary, lw[-match_len:-1] + chr(ord(lw[-1])+1))
        #print(left, right)
        for r, rw in enumerate(dictionary[left:right]):
            if(visited[r]):
                continue
            r += left
            
            prefix_len = halves[r]

            match = single_calc(suffix_len, prefix_len)

            #print("testing '" + rw + "'")

            #check if suffix matches prefix of next word
            if(lw[-match:] == rw[0:match]):
                #print("queued '" + rw + "'")
                #visit node
                a_map[r] = l
                distance[r] = distance[l] + 1
                #save the neighbour to the return list
                neighbours[count] = r
                count += 1
            #print("rejected '" + rw + "'")

        
    return neighbours[:count]


@memoize
def single_calc(l, r):
    return min(l, r)

@memoize
def double_calc(l, r):
    return max(l, r)


def find_neighbours_double(dictionary, visited, distance, halves, a_map, l):
    lw = dictionary[l]
    #minimum length of the matching part of the left word
    suffix_len = halves[l]

    neighbours = np.zeros(len(dictionary), dtype=int)
    count = 0

    #check how big the matching string must be
    #min_len = double_calc(suffix_len, len(lw))

    for match_len in range(suffix_len, len(lw)):
        left = bisect(dictionary, lw[-match_len:])
        right = bisect(dictionary, lw[-match_len:-1] + chr(ord(lw[-1])+1))
        #print("matching a suffix of", lw[-match_len:])
        for r, rw in enumerate(dictionary[left:right]):
            if(visited[r]):
                continue
            
            r += left   

            prefix_len = halves[r]

            match = double_calc(suffix_len, prefix_len)

            #check if suffix matches prefix of next word
            if(lw[-match:] == rw[0:match]):
                #visit node
                a_map[r] = l
                distance[r] = distance[l] + 1
                #save the neighbour to the return list
                neighbours[count] = r
                count += 1

        
        
    return neighbours[:count]


if __name__ == "__main__":
    main()