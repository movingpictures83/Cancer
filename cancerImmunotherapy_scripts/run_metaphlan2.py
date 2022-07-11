import os
import subprocess

#SAMPLES_FOLDER="/biorg/references/bacteria/samples/cancerImmunotherapy"

def run_metaphlan2(m1, m2, outdir):
    command = "metaphlan2 " + m1 + "," + m2 + " " \
              "--input_type multifastq \
                -nproc 24 \
                --no-map \
                > " + outdir
    subprocess.call(command)
    return

PROJECT_DIR="/biorg/references/bacteria/cancerImmunotherapy"
SAMPLES_FOLDER=PROJECT_DIR + "/samples"
OUT_DIR = PROJECT_DIR + "/results"

samples=os.listdir(SAMPLES_FOLDER)

sample = "663-002_End_of_Treatment_S72_L008"

m1 = sample + "_R1_001.fastq"
m2 = sample + "_R2_001.fastq"
m1=os.path.join(SAMPLES_FOLDER, m1)
m2=os.path.join(SAMPLES_FOLDER, m2)

out = OUT_DIR + "/" + sample + "_abundance.txt"

run_metaphlan2(m1, m2, out)
