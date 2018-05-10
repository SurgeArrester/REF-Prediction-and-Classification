import java.io.IOException;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;


public class IntSumReducer
		extends Reducer<Text,IntWritable,Text,IntWritable> {
	private IntWritable result = new IntWritable(); // Make an int called result that has the sum
	
	public void reduce(Text key, // The keys from our context 
					   Iterable<IntWritable> values, // The values from our context
	                Context context // The address (?) of our context
	                ) throws IOException, InterruptedException {
		int sum = 0;
		for (IntWritable val : values) { // Loop through the keys in the context
			sum += val.get();			   // Sum up the ones associated with each key
		}
			result.set(sum);				   // Set result to equal sum (convert from int to IntWritable)
			context.write(key, result);	   // Create a new hashtable of key: result
	}
}
