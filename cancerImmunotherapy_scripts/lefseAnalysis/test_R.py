import os,sys,math,pickle
import random as lrand
import rpy2.robjects as robjects
import argparse
import numpy
#import svmutil

def init():
    lrand.seed(1982)
#    robjects.r('.libPaths( c( .libPaths(), "/Library/Frameworks/R.framework/Versions/3.6/Resources/library"))')
    robjects.r('library(splines)')
    robjects.r('library(stats4)')
    robjects.r('library(survival)')
    robjects.r('library(mvtnorm)')
    robjects.r('library(modeltools)')
    robjects.r('library(coin)')
    robjects.r('library(MASS)')


#init()
#robjects.r('.libPaths( c( .libPaths(), "/Library/Frameworks/R.framework/Versions/3.6/Resources/library"))')

print(robjects.r('.libPaths()'))
print(robjects.r('.libPaths()'))

#robjects.r('install.packages("survival")')
# from rpy2.robjects.packages import importr
# utils = importr('utils')
# utils.install_packages('survival')
