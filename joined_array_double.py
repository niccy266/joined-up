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
    global dictionary, SINGLE, DOUBLE

    SINGLE = True
    DOUBLE = False
    
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
        
        single_len = bfs(dictionary, halves, SINGLE, start, end)
        print(*single_len)
        double_len = bfs(dictionary, halves, DOUBLE, start, end)
        print(*double_len)

    sys.exit(0)


def end_has_no_links(d, end, match_calc, min_len):
    
    #reverse end
    end = end[::-1]
    suffix_len = int((len(end) + 1) / 2)

    #reverse all words
    reverse_dict = [w[::-1] for w in d]
    reverse_dict.sort()

    for match_len in range(min_len, len(end) + 1):
        
        left = bisect(reverse_dict, end[-match_len:])
        right = bisect(reverse_dict, end[-match_len:-1] + chr(ord(end[-1])+1))
        
        for r, rw in enumerate(reverse_dict[left:right]):

            r += left

            #check if the suffix we are checking is long enough to join for either word
            prefix_len = int((len(rw) + 1) / 2)
            match = match_calc(suffix_len, prefix_len)
            if (match_len < match):
                continue

            #check if suffix matches prefix
            if(end[-match:] == rw[:match]):
                #print("found", rw[::-1])
                return False
    #print("found no double links to finish at hyper")
    return True


def bfs(d, halves, link_type, start_i, end_i):
    SINGLE, DOUBLE

    end = d[end_i]

    if link_type == SINGLE and end_has_no_links(d, end, single_calc, 1):
        return [0]
    if link_type == DOUBLE and end_has_no_links(d, end, double_calc, halves[end_i]):
        return [0]

    visited = np.array([False] * len(d), dtype=bool)
    distance = np.array([100000] * len(d), dtype=int)

    #visit the start node
    distance[start_i] = 1
    visited[start_i] = True

    #hashmap = dict.fromkeys(dictionary)
    a_map = np.array([-1] * len(d), dtype=int)

    #queue the starting node and start the search
    q = queue.Queue(len(d))
    #print("Initialising the queue with starting word", dictionary[start_i])
    q.put(start_i)
    #while stack still has items
    while(not q.empty()):
        l = q.get()

        if link_type == SINGLE:
            neighbours = find_neighbours_single(d, visited, distance, halves, a_map, l)
        else:
            neighbours = find_neighbours_double(d, visited, distance, halves, a_map, l)
        
        for i in neighbours:
            if(i == end_i):
                r = i
                #create a list of words joining start and end to return
                out = [distance[r], d[r]]
                while(a_map[r]!= -1):
                    r = a_map[r]
                    out.insert(1, d[r])

                return out
            
            q.put(i)
            visited[i] = True

    #didn't find a chain
    return [0]


@memoize
def single_calc(l, r):
    return min(l, r)

@memoize
def double_calc(l, r):
    return max(l, r)
    
@memoize
def start_index(item) :
    return bisect(dictionary, item)


def find_neighbours_single(dictionary, visited, distance, halves, a_map, l):
    lw = dictionary[l]
    #minimum length of the matching part of the left word
    suffix_len = halves[l]

    neighbours = np.array([-1] * len(dictionary), dtype=int)
    count = 0


    for match_len in range(1, len(lw) + 1):
        #print("matching strings of length", match_len)
        left = start_index(lw[-match_len:])
        right = start_index(lw[-match_len:-1] + chr(ord(lw[-1])+1))
        #print(left, right)
        for r, rw in enumerate(dictionary[left:right]):
            r += left
            
            if(visited[r]):
                continue

            prefix_len = halves[r]

            match = single_calc(suffix_len, prefix_len)

            if(match_len < match):
                #continue
                pass

            #check if suffix matches prefix
            if(lw[-match_len:] == rw[0:match_len]):
                #print("queued '" + rw + "'")
                #visit node
                a_map[r] = l
                distance[r] = distance[l] + 1
                #save the neighbour to the return list
                neighbours[count] = r
                count += 1
            #print("rejected '" + rw + "'")

        
    return neighbours[:count] if neighbours[0] != -1 else []


def find_neighbours_double(dictionary, visited, distance, halves, a_map, l):
    lw = dictionary[l]
    #minimum length of the matching part of the left word
    suffix_len = halves[l]
    #left_len = len(lw)

    neighbours = np.zeros(len(dictionary), dtype=int)
    count = 0

    #check how big the matching string must be
    #min_len = double_calc(suffix_len, len(lw))
    #print(lw)
    for match_len in range(suffix_len, len(lw) + 1):
        #print("matching strings of length", match_len)
        left = start_index(lw[-match_len:])
        right = start_index(lw[-match_len:-1] + chr(ord(lw[-1])+1))
        #print("matching a suffix of", lw[-match_len:])
        for r, rw in enumerate(dictionary[left:right]):
            r += left   

            if(visited[r]):
                continue
            
            if(len(rw) < suffix_len):
                continue

            prefix_len = halves[r]

            match = double_calc(suffix_len, prefix_len)

            if(match_len < match):
                continue

            #check if suffix matches prefix of next word
            if(lw[-match_len:] == rw[0:match_len]):
                #visit node
                a_map[r] = l
                distance[r] = distance[l] + 1
                #save the neighbour to the return list
                neighbours[count] = r
                count += 1
        
    return neighbours[:count]# if neighbours[0] != -1 else []


if __name__ == "__main__":
    main()