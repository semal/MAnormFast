this is a README of python-version MAnorm command tool
if you has any question, you could contact us by email: gzhsss2@gmail.com

**Input**
There are four input files needed, 2 peaks files and 2 reads files:
    python MAnorm.py --p1 peak1 --r1 read1 --p2 peak2 --r2 read1
peak file support bed format and macs output xls format. The first three columns
should be ‘chr start end’ , if there are summit column, should put it in fourth
cloumn.

**Other Options**
There are 9 options left for regulating the programe.
-n or --random_test: number of random permutations to test the enrichment of overlapping between two peak sets, default=5.
-e or --extension: default=1000, 2*extension=size of the window centered at peak summit to calculate reads density. The window size should match the typical length of peaks, thus we recommend extension=1000 for sharp histone marks like H3K4me2/3 or H3K9/27ac, extension=500 for transcription factor or DNase-seq.
-d or --summit2summit_dist: summit to summit distance cutoff,  default=extension/2. Only those common peaks with distance between their summits in 2 samples smaller than this value will be considered as real common peaks for building the normalization model.
-o or --output: Name of this comparison, which will be also used as the name of folder created to store all output files, default is "MAnorm_pair".
-v or --overlap_independent: By default, MAnorm will choose biased peaks only from unique peaks, and choose unbiased peaks only from common peaks. But if this option is used, MAnorm will choose biased and unbiased peaks just based on the M-value and P-value cutoffs, without checking whether they are common or unique peaks.
-p or --pcut_biased: Cutoff of P-value to define biased (high-confidence sample 1 or 2-specific) peaks, default=0.01.
-m or --mcut_biased: Cutoff of M-value to define biased peaks, default=1. Sample 1 biased peaks are defined as sample 1 unique peaks with M-value > mcut_biased and P-value < pcut_biased, while sample 2 biased peaks are defined as sample 2 unique peaks with M-value < -1*mcut_biased and P-value < pcut_biased.
-u or --mcut_unbiased: Cutoff of M-value to define unbiased (high-confidence non-specific) peaks between 2 samples, default=1. They are defined to be the common peaks with -1*mcut_unbiased < M-value < mcut_unbiased and P-value > pcut_biased.
-s or --no_merging: By default, MAnorm will first separate both sets of input peaks into common and unique peaks, by checking whether they have overlap with any peak in the other sample, and then merge the 2 sets of common peaks into 1 group of non-overlapping ones. But if this option is used, MAnorm won’t merge the common peaks, and the peaks in output files will be exactly the same as those from input.

**Output files**
the directory name of output folder is named by ‘ -o or –ouput’ option. default name
is ‘MAnorm_pair’ . There are three folders under this directory, they are
‘output_figures’ , ‘output_tables’ and ‘output_wigfiles’ . Just like:
** MAnorm_pair
    *output_figures
    *output_tables
    *output_wigfiles

the output_figures folder including 4 png files, they are ‘before_rescale.png’ , ‘after_rescale.png’ , ‘ log2_read_density.png’ and ‘ -log10_P-value.png’ . the ‘ log2_read_density.png’ is the fitting model of common peaks. ‘before_rescale.png’ and ‘after_rescale.png’ show the peaks situation before and after MAnorm. ‘ -log10_P-value.png’ show the pvalue situation after MAnorm.