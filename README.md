## Introduction

ChIP-Seq is widely used to characterize genome-wide binding patterns of transcription factors and other chromatin-associated proteins. Although comparison of ChIP-Seq data sets is critical for understanding cell type-dependent and cell state-specific binding, and thus the study of cell-specific gene regulation, few quantitative approaches have been developed. 

Here, we present a simple and effective method, MAnorm, for quantitative comparison of ChIP-Seq data sets describing transcription factor binding sites and epigenetic modifications. The quantitative binding differences inferred by MAnorm showed strong correlation with both the changes in expression of target genes and the binding of cell type-specific regulators.

## Command

**Input:**
There are five input arguments needed, 2 peaks files and 2 reads files, and ouptut folder name:
    
    python MAnorm.py --p1 peak1 --r1 read1 --p2 peak2 --r2 read1 -o ouput_folder_name

**Note:** peak file support bed format and macs output xls format. The first three columns 
should be ‘chr start end’ , if there are summit column, should put it in fourth cloumn.

**Other Options:**
> **Note:** Using --help for seeing details.

**More**
http://semal.cn:2013/

## Installation

1. python setup.py install for pacakge installation.
2. add /bin/MAnormFast script to PATH and chmod -x MAnormFast for excutive function.
3. you could use MAnormFast as a command alreay.

Good luck.

> if you has any question, you could contact us by email: gzhsss2@gmail.com

semal

## Reference

And if you want to know the detail of this model, you could download the article:

[Shao Z, Zhang Y, Yuan GC, Orkin SH, Waxman DJ. (2012) MAnorm: a robust model for quantitative comparison of ChIP-Seq data sets. Genome Biol. Mar 16;13(3):R16.](https://genomebiology.biomedcentral.com/articles/10.1186/gb-2012-13-3-r16)

