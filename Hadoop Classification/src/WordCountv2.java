import java.io.IOException;
import java.io.File;

import org.apache.commons.io.FileUtils;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;

import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.SequenceFileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.SequenceFileOutputFormat;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;

class WordCountv2 {
	public static void main(String[] args) throws Exception {
		Configuration conf = new Configuration();
        org.apache.log4j.BasicConfigurator.configure(); // Set the logging function to output to the console

        String[] folderNames = {"Chemistry",
    		  				    "GeneralEngineering",
    		  				    "Geography,EnvironmentalStudiesandArchaeology",
    		  				    "Physics",
    		  				    "MathematicalSciences",
    		  				    "ComputerScienceandInformatics",
    		  				    "ElectricalandElectronicEngineering,MetallurgyandMaterials"};

        // Loop through the assorted folders, delete the content then process the csv titles
		for (String folder : folderNames) {
			File out = new File(args[1] + "/" + folder); // Create filepath to be used
			FileUtils.deleteDirectory(out);		// from org.apache.commons.io.FileUtils;

            Job job1 = Job.getInstance(conf, "word count");
	  		job1.setJarByClass(WordCountv2.class);

	  		job1.setMapperClass(TokenizerMapper.class);		// Perform standard wordcount operation on the file and
	  		job1.setCombinerClass(SumReducer.class);		// save as a sequence file, NOT text
	  		job1.setReducerClass(SumReducer.class);
	  		job1.setOutputKeyClass(Text.class);
	  		job1.setOutputValueClass(LongWritable.class);
	  		job1.setOutputFormatClass(SequenceFileOutputFormat.class);

	  		FileInputFormat.addInputPath(job1, new Path(args[0] + "/" + folder));
	  		FileOutputFormat.setOutputPath(job1, new Path(out + "/out1"));	// Save in an intermediate place

	  		job1.waitForCompletion(true);

	  		Job job2 = Job.getInstance(conf, "Frequency Distribution");		// Create second mapred job to sort by the values
	  		job2.setJarByClass(WordCountv2.class);							// as opposed to keys

	  		job2.setMapperClass(KeyValueSwappingMapper.class);
	  		job2.setNumReduceTasks(1);										// This uses the sorting method of reduce without reduction
	  		job2.setSortComparatorClass(LongWritable.DecreasingComparator.class);

	  		job2.setOutputKeyClass(LongWritable.class);
	  		job2.setOutputValueClass(Text.class);
	  		job2.setInputFormatClass(SequenceFileInputFormat.class);

	  		FileInputFormat.addInputPath(job2, new Path(out + "/out1"));    // Pull the file from our previous folder and save to
	  		FileOutputFormat.setOutputPath(job2, new Path(out + "/out2"));  // new folder

	  		if (!job2.waitForCompletion(true) && folder == folderNames[folderNames.length - 1]) { // On the final topic, exit
	  		  System.exit(1);
	  		}
		}
	}

	public static class TokenizerMapper
	    extends Mapper<Object, Text, Text, LongWritable> {

	    private static Text word = new Text();
	    private final static LongWritable one = new LongWritable(1);

	    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
	        String line = value.toString().replace("\"", "").toLowerCase();
	        String[] items = line.split(" ");
	        for (String item : items) {
	       	 item.replace("'", "");
	            word = new Text(item);
	            context.write(word, one);
		    }
	    }
	}

	public static class SumReducer
		extends Reducer<Text, LongWritable, Text, LongWritable> {

	    private LongWritable result = new LongWritable();

	    public void reduce(Text key, Iterable<LongWritable> values, Context context) throws IOException,
	        InterruptedException {
	    	long sum = 0;
	    	for (LongWritable val : values) {
	    		sum += val.get();
	    	}

	    	result.set(sum);
	    	context.write(key, result);
	    }
	}

	public static class KeyValueSwappingMapper
		extends Mapper<Text, LongWritable, LongWritable, Text> {

		public void map(Text key, LongWritable value, Context context) throws IOException, InterruptedException {
		      context.write(value, key);
	    }
	}
}
