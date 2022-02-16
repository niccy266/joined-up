import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.Scanner;
import java.util.Set;

public class Joined {  
    public static String[] dictionary;
    public static Node[] graph;
    public static String start;
    public static String end;
    public static Node startN;
    public static Node endN;
    //public static Node current;
    public static Queue<Node> q;
    // signed integer limit, but 1000000 would be fine
    //public static final int MAX = 2147483647; 

    public static void main(String[] args) {
        try {
            start = args[0];
            end = args[1];
        } catch(IndexOutOfBoundsException e) {
            System.out.println("please give two words to join in args");
            System.exit(1);
        }

        loadDict();

        System.out.println(start + " " + end);

        if (start == end) {
            System.out.println("1 " + start + " " + end);
            System.out.println("1 " + start + " " + end);
        } else {
            System.out.println("Searching for single link chain");
            bfs(new Single());
            System.out.println("printing path " + endN.distance);
            printPath(endN);
            System.out.println("Searching for double link chain");
            bfs(new Double());
            System.out.println("1 " + start + " " + end);
            printPath(endN);
        }
    }


    /**
     * Reads in the dictionary words from standard input
     * @return sorted dictionary as an array
     */
    public static void loadDict() {
        // set to avoid duplicates
        Set<String> temp = new LinkedHashSet<String>();
        Scanner sc = new Scanner(System.in);
        if(!sc.hasNext()) {
            System.out.println("please pass a dictionary to standard input");
            System.exit(1);
        }

        do {
            temp.add(sc.nextLine().strip().toLowerCase());
        } while (sc.hasNextLine());
        sc.close();
    
        // make sure start and target worda are in dictionary by adding them
        temp.add(start);
        temp.add(end);

        // convert dictionary to list so it can be sorted alphabetically
        List<String> temp2 = new LinkedList<String>(temp);
        Collections.sort(temp2);
        dictionary = new String[temp2.size()];
        for(int i = 0; i < dictionary.length; i++){
            dictionary[i] = temp2.get(i);
            System.out.println(dictionary[i]);
        }
        graphFromDict();
        // save the index of the start and end word for ease of access
        endN = graph[temp2.indexOf(end)]; 
        startN = graph[temp2.indexOf(start)]; 
    }


    private static void graphFromDict() {
        graph = new Node[dictionary.length];
        for(int i = 0; i < graph.length; i++) {
            graph[i] = new Node(i, dictionary[i]);
        }
    }


    public static void bfs(Matcher m) {
        resetGraph();

        q = new LinkedList<Node>();
        q.add(startN);
        System.out.println("visiting start node");
        startN.visit(0);
        List<Node> n;

        do {
            Node l = q.poll();
            System.out.println("processing " + l.word);
            n = queueNeighbours(l, m);
            for(Node node : n) {
                if(node == endN) {
                    System.out.println("found the end " + node.word);
                    return;
                }
                System.out.println("queueing " + node.word);
                q.add(node);
            }
            System.out.println(q.peek());
        } while(!q.isEmpty());
        
        System.out.println("queue was empty");
    }


    private static List<Node> queueNeighbours(Joined.Node l, Joined.Matcher m) {
        List<Node> n = new LinkedList<Node>();
        String lw = l.word;
        Node r;
        String suffix;
        int min =  m.minLen(l);

        char lastChar = lw.charAt(l.len_ - 1);
        char lastCharPlus1 = (char) (lastChar + 1);
        for(int i = min - 1; i < l.len_ - 1; i++) {
            suffix = getSuffix(l, i);

            int start = bisect(dictionary, suffix + lastChar);
            int end = bisect(dictionary, suffix + lastCharPlus1);
            
            System.out.println(suffix + lastChar);
            System.out.println(suffix + lastCharPlus1);
            System.out.println(start + " " + end);
    
            for(int j = start; j < end; j++) {
                r = graph[i];
                if(r.visited) {
                    System.out.println("already visited " + r.word);
                    continue;
                }
                
                System.out.println("testing matches: " + r.word);
                if(m.matches(l, r, i)) {
                    r.visit(l);
                    n.add(r);
                }
            }
        }
        return n;
    }


    /**
     * Returns the result of Arrays.binarySearch, but made positive
     * If an item isn't found in a binary search the old function
     * returns a negative number but instead i have made it positive
     * @param a array
     * @param s Word to search for
     * @return a positive index where the item 
     */
    public static int bisect(String[] a, String s) {
        int i = Arrays.binarySearch(dictionary, s);
        return (i < 0) ? -i : i;
    }


    public static String getSuffix(Node l, int i) {
        if(i < 1) return "";
        return l.word.substring(l.len_ - i - 1, l.len_ - 1);
    }


    private static void resetGraph() {
        for(Node n : graph) {
            n.visited = false;
            n.distance = 0;
            n.root = null;
        }
    }

    public static class Node{
        int index;
        String word;
        boolean visited = false;
        int distance;
        Node root;
        int len_;
        int half;

        public Node(int i, String w) {
            index = i;
            word = w;
            len_ = word.length();
            half = (len_ + 1) / 2;
        }

        public void visit(Joined.Node l) {
            visit(l.distance + 1);
            root = l;
        }

        public void visit(int i) {
            visited = true;
            distance = i;
            System.out.println(word + ": I was visited; " + distance);
        }

        public boolean equals(String s) {
            return s.equals(word);
        }
    }
    

    public static int max(int l, int r) {
        return (l > r) ? l : r;
    }
    public static int min(int l, int r) {
        return (l < r) ? l : r;
    }


    public static interface Matcher {
        public boolean matches(Node l, Node r, int matchLen);

        public int minLen(Node l);
    }


    public static class Single implements Matcher {
        public boolean matches(Node l, Node r, int matchLen){
            return checkMatch(l, r, minLen(l));
        }

        public static boolean checkMatch(Node l, Node r, int min) {
            String match;
            for(int i = min; i < min(l.len_, r.len_); i++){
                match = l.word.substring(l.len_ - i, l.len_);
                System.out.println("trying to match " + match + " and " + 
                                r.word.substring(0, i));
                if(match.equals(r.word.substring(0, i))) {
                    
                    return true;
                }
            }
            return false;
        }

        public int minLen(Node l){
            return 1;
        }
    }

    public static class Double extends Single{        
        public int minLen(Node l){
            return l.half;
        }
    }


    private static void printPath(Node n) {
        System.out.print(n.distance);
        for(int i = n.distance; i > 2; i--) {
            System.out.print(" " + n.word);
            n = n.root;
        }
        System.out.println();
    }
}
