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


## Peak file format support

standard bed format is supported. and there are 3 other kinds of peak file format supported by MAnormFast, 3-col tab split format, 4-col tab split format and MACS peak file. 3-col including peak chromosome, peak start and peak end.

### 3-columns tab split format

```
chr1  2345  4345
chr1  3456  5456
chr2  6543  8543 
```

### 4-columns tab split format

```
chr1  2345  4345  254
chr1  3456  5456  127
chr2  6543  8543  302
```

### MACS output peak file

```
# This file is generated by MACS
# ARGUMENTS LIST:
# name = A549_H3K27acEtoh02_Rep1
# format = BED
# ChIP-seq file = /mnt/MAmotif/1.RAWdata/Histone_Broad_hg19/H3K27ac/wgEncodeBroadHistoneA549H3k27acEtoh02AlnRep1.bed
# control file = /mnt/MAmotif/1.RAWdata/Histone_Broad_hg19/modified_control/wgEncodeBroadHistoneA549ControlEtoh02AlnRep2.bed
# effective genome size = 3.14e+09
# tag size = 37
# band width = 300
# model fold = 32
# pvalue cutoff = 1.00e-05
# Ranges for calculating regional lambda are : peak_region,1000,5000,10000
# unique tags in treatment: 28191481
# total tags in treatment: 32226999
# unique tags in control: 27551475
# total tags in control: 32964797
# d = 200
chr     start   end     length  summit  tags    -10*log10(pvalue)       fold_enrichment FDR(%)
chr7    97911064        97917104        6041    368     648     3233.06 22.57   0.0
chr11   35159640        35167695        8056    1358    1066    3233.06 21.83   0.0
chr7    156684099       156687307       3209    2242    526     3233.06 43.37   0.0
chrX    55025266        55028474        3209    1270    551     3233.06 36.65   0.0
chr17   592847  601584  8738    4484    1286    3233.06 19.17   0.0
chr4    985500  988137  2638    1351    412     3233.06 34.69   0.0
```


## Reference

And if you want to know the detail of this model, you could download the article:

[Shao Z, Zhang Y, Yuan GC, Orkin SH, Waxman DJ. (2012) MAnorm: a robust model for quantitative comparison of ChIP-Seq data sets. Genome Biol. Mar 16;13(3):R16.](https://genomebiology.biomedcentral.com/articles/10.1186/gb-2012-13-3-r16)

