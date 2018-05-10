import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

class mapper {

	public static class TokenizerMapper
        extends Mapper<Object, Text, Text, IntWritable>{

    private final static IntWritable one = new IntWritable(1); // Assign one to the constant 1

	private Text word = new Text();	// Private variable to store each word
	
	public void map(Object key, 
					Text value, 
					Context context
					) throws IOException, InterruptedException {
	    StringTokenizer itr = new StringTokenizer(value.toString(),","); // Take in the corpus as a string, splits on commas
	  
	    while (itr.hasMoreTokens()) {
		    word.set(itr.nextToken().toLowerCase().trim()); // Assign the next word to our word variable]
	
	    String[] items = word.toString().split(" "); //.asList(word.split("\\s*,\\s*"));
	    for (String item: items) {
		    word = new Text(item);
		    context.write(word, one);  // Pass {"word": 1} to our context (?)
	    }
	  }
    }
  }
}
    
