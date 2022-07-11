# Running the LEfSe commands with -h gives the list of available options

# format_input.py convert the input data matrix to the format for LEfSe.
#
# In this example we use the class information in the first line (-c 1)
# no subclass and the subject in the second (-u 2).
# -o 100000000 scales the feature such that the sum (of the same taxonomic leve)
# is 100M: this is done only for obtaining more meaningful values for the LDA score
../format_input.py S-ADHD.txt S-ADHD.in -c 1 -u 2 -o 1000000

# run_lefse.py performs the actual statistical analysis
#
# Apply LEfSe on the formatted data producing the results (to be further processed
# for visualization with the other modules). The option available
# can be listed using the -h option 
../run_lefse.py S-ADHD.in S-ADHD.res

# plot_res.py visualizes the output
#
# Plot the list of biomarkers with their effect size
# Severak graphical options are available for personalizing the output
../plot_res.py S-ADHD.res S-ADHD.png --dpi 600

# plot_cladogram.py visualizes the output on a hierarchical tree
#
# Plot the representation of the biomarkers on the hierarchical tree
# specified in the input data (using | in the name of the features)
# In this case we will obtain the RDP taxonomy.
# This is an early implementation of the module. I'm working on an improved version
# that will be released independently from LEfSe
../plot_cladogram.py S-ADHD.res S-ADHD.cladogram.png --format png --dpi 600

# Create a directory for storing the raw-data representation of the discovered biomarkers
mkdir biomarkers_raw_images_S

# plot_features.py visualizes the raw-data features
#
# The module for exporting the raw-data representation of the features.
# With the default options we will obtain the images for all the features that are
# detected as biomarkers
../plot_features.py S-ADHD.in S-ADHD.res biomarkers_raw_images_S/


