//// Simply the introductory wordcount program as supplied in the lectures
//
//import java.io.IOException;
//import java.util.List;
//import java.util.StringTokenizer;
//import java.io.File;
//import java.util.Arrays;
//
//import org.apache.hadoop.conf.Configuration;
//import org.apache.hadoop.fs.Path;
//import org.apache.hadoop.io.IntWritable;
//import org.apache.hadoop.io.Text;
//import org.apache.hadoop.mapreduce.Job;
//import org.apache.hadoop.mapreduce.Mapper;
//import org.apache.hadoop.mapreduce.Reducer;
//import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
//import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
////
////import IntSumReducer.IntSumReducer;
//import mapper.TokenizerMapper;
//
//class mainClass {
//	public static void main(String[] args) throws Exception {
//    //BasicConfigurator.configure();
//	    Configuration conf = new Configuration();
//	    org.apache.log4j.BasicConfigurator.configure(); // Set the logging function to just output to the console
//	    Job job = Job.getInstance(conf, "word count");
//	    
//	    System.out.print(args[0]);
//	    
//	    job.setJarByClass(WordCount.class);
//	    job.setMapperClass(mappper.TokenizerMapper.class);
//	    job.setCombinerClass(IntSumReducer.class);
//	    job.setReducerClass(IntSumReducer.class);
//	    
//	    job.setOutputKeyClass(Text.class);
//	    job.setOutputValueClass(IntWritable.class);
//	    
//	    // Open the output folder and delete the contents if necessary
//	    File index = new File(args[1]); 
//	    if (index.exists()) {
//	    	System.out.print("Folder Exists");
//	        String[] entries = index.list();
//	        for(String s: entries) {
//		        File currentFile = new File(index.getPath(),s);
//		        currentFile.delete();
//	        }
//	        index.delete();
//	    }
//	    
//	    FileInputFormat.addInputPath(job, new Path(args[0]));
//	    FileOutputFormat.setOutputPath(job, new Path(args[1]));    
//	    
//	    System.exit(job.waitForCompletion(true) ? 0 : 1);
//	}
//}
