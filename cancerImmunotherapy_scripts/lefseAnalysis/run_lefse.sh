#!/bin/bash

# Home directories:

# Path to downloaded from source lefse app:
#LEFSE_PATH="/Users/stebliankin/Desktop/apps/lefse"
#
#DATA_DIR="/Users/stebliankin/Desktop/FLINTproject/cancerImmunotherapy/results/classData"

# Castalia Directories:
LEFSE_PATH="/lclhome/vsteb002/apps/nsegata-lefse-82605a2ae7b7"
DATA_DIR="/lclhome/vsteb002/cancerImmunotherapy_scripts/results/classData"

#FILENAME="Abund-PFSlow-hi"
FILENAME="Abund-PFSlow-veryhi"
#FILENAME="Abund-CRPRSD-PD"

DATA_PATH=$DATA_DIR"/"$FILENAME".txt"


LEFSE_IN=$DATA_DIR"/"$FILENAME".in"
RES_FILE=$DATA_DIR"/"$FILENAME".res"

PNG_FILE=$DATA_DIR"/"$FILENAME".png"


# Convert the input data matrix to the LEFSe format:

# In this example we use the class information in the first line (-c 1)
# no subclass and the subject in the second (-u 2).
# -o 100000000 scales the feature such that the sum (of the same taxonomic leve)
# is 100M: this is done only for obtaining more meaningful values for the LDA score
python2 $LEFSE_PATH"/format_input.py" $DATA_PATH $LEFSE_IN -c 1 -s -1 -u 2 -o 1000000

#run_lefse.py performs the actual statistical analysis
#
# Apply LEfSe on the formatted data producing the results (to be further processed
# for visualization with the other modules). The option available
# can be listed using the -h option

#source activate py2
python2 $LEFSE_PATH"/run_lefse.py" $LEFSE_IN $RES_FILE


# plot_res.py visualizes the output
#
# Plot the list of biomarkers with their effect size
# Severak graphical options are available for personalizing the output
python2 $LEFSE_PATH"/"plot_res.py $RES_FILE $PNG_FILE --dpi 600
