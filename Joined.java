import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Scanner;
import java.util.Set;

public class Joined {  
    public static String[] dictionary;
    public static Node[] graph;
    public static String start;
    public static String end;

    public static void main(String[] args) {
        try {
            start = args[0];
            end = args[1];
        } catch(IndexOutOfBoundsException e) {
            System.out.println("please give two words to join in args");
            System.exit(1);
        }

        dictionary = loadDict();
        graph = graphFromDict();
        

        System.out.println(start + " " + end);

        if (start == end) {
            System.out.println("1 " + start + " " + end);
            System.out.println("1 " + start + " " + end);
        }
    }

    private static Node[] graphFromDict() {
        graph = new Node[dictionary.length];
        
        for(int i = 0; i < graph.length; i++) {
            graph[i] = new Node(i, dictionary[i]);
        }
        return graph;
    }

    /**
     * Reads in the dictionary words from standard input
     * @return sorted dictionary as an array
     */
    public static String[] loadDict() {
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
    
        // make sure target word is in the dictionary by adding it
        temp.add(end);

        // convert dictionary to list so it can be sorted alphabetically
        List<String> temp2 = new LinkedList<String>(temp);
        Collections.sort(temp2);
        return (String[]) temp2.toArray();
    }

    public static class Node{
        int index;
        String word;
        boolean visited = false;
        int distance;
        Node root;
        int length;
        int half;

        Node(int i, String w) {
            index = i;
            word = w;
            length = word.length();
            half = (w.length() + 1) / 2;
            distance = 2147483647; // signed integer limit
        }
    }
}
