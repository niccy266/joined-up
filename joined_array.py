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

    halves = calc_halves(dictionary)

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


def calc_halves(d):
    halves = []
    for w in d :
        halves.append(int((len(w) + 1) / 2))
    return np.array(halves, dtype=int)


def end_has_no_links(d, end_i, link_type):
    end = d[end_i]
    end_len = len(end)
    suffix_len = int((end_len + 1) / 2)

    if link_type == SINGLE:
        match_calc = single_calc
        min_len = 0
    else:
        match_calc = double_calc
        min_len = suffix_len

    #reverse all words
    end = end[::-1]
    reverse_dict = [w[::-1] for w in d]
    reverse_dict.sort()

    for match_len in range(min_len, end_len + 1):
        print("finding all words starting from", end[-match_len:][::-1], "to", (end[-match_len:-1] + chr(ord(end[-1])+1))[::-1])
        left = bisect(reverse_dict, end[-match_len:]) - 1
        right = bisect(reverse_dict, end[-match_len:] + chr(ord(end[-1])+1)) + 1
        print(left, right)

        for r, rw in enumerate(reverse_dict[left:right]):

            r += left

            #check if the suffix we are checking is long enough to join for either word
            prefix_len = int((len(rw) + 1) / 2)
            match = match_calc(suffix_len, prefix_len)
            
            if (match_len < match):
                #continue
                pass

            #check if suffix matches prefix
            if(end[-match_len:] == rw[0:match_len]):
                print("found", rw[::-1])
                return False
            print("rejected", rw[::-1])
            print(end[-match_len:] + " " + rw[0:match_len])
            print(len(end[-match_len:]), len(rw[0:match_len]))

    #print("found no double links to finish at hyper")
    return True


def bfs(d, halves, link_type, start_i, end_i):

    if end_has_no_links(d, end_i, link_type):
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
            n = find_neighbours(d, visited, distance, halves, a_map, l, single_calc, 0)
        else:
            n = find_neighbours(d, visited, distance, halves, a_map, l, double_calc, halves[l])
        
        for i in n:
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


def find_neighbours(dictionary, visited, distance, halves, a_map, l, match_method, start):

    lw = dictionary[l]
    #minimum length of the matching part of the left word
    suffix_len = halves[l]

    neighbours = np.array([-1] * len(dictionary), dtype=int)
    count = 0

    for match_len in range(start, len(lw) + 1):

        left = bisect(dictionary, lw[-match_len:])
        right = bisect(dictionary, lw[-match_len-1:] + chr(ord(lw[-1])+1))

        for r, rw in enumerate(dictionary[left:right]):
            r += left
            
            if(visited[r]):
                continue
            
            if len(rw) > 2 * match_len:
                continue

            prefix_len = halves[r]

            match = match_method(suffix_len, prefix_len)

            if(match_len < match):
                match_len = match

            #check if suffix matches prefix
            if(lw[-match_len:] == rw[0:match_len]):
                #visit node
                a_map[r] = l
                distance[r] = distance[l] + 1
                #save the neighbour to the return list
                neighbours[count] = r
                count += 1

    
        
    return neighbours[:count] # if neighbours[0] != -1 else []


if __name__ == "__main__":
    main()

#comment