# Guide to genomic reference material in Bento

This document includes a bit of information on what a reference genome is, what some common ones for Bento projects are,
and some subtleties that are **important to pay attention to.**


## Table of Contents

* [What is a reference genome?](#what-is-a-reference-genome)
* [File representation of reference genomes](#file-representation-of-reference-genomes)
* [Common reference genomes](#common-reference-genomes)
* [Aspects to pay attention to!](#aspects-to-pay-attention-to)


## What is a reference genome?

Organisms of the same species share the vast majority of their DNA sequence, with variation in phenotype (appearance, 
behaviour, disease susceptibility, etc.) being to a large extent the result of variation in specific loci (regions)
of the individuals' genome.

As a result, bioinformatics file formats often (but not always!) use a common set of sequences called a 
"reference genome", and data is associated with a particular chromosome and position within this genome.

As an example, one reference genome for humans is called "hg38"/"GRCh38". Human individuals usually have 46 chromosomes:
22 pairs of autosomes, and 1 pair of sex chromosomes (n = (22 + 1); 2n = 46 - see Figure 1). One copy of each chromosome
is inherited from an individual's mother, the other from their father. The `hg38` reference genome has 24 main genomic 
sequences: `chr1`-`chr22` + `chrX` + `chrY` (Table 1); we don't need pairs here, since the pairs are extremely similar
to one another; any variation between them can (usually) be well-represented 

> ![A karyotype of a human male](https://upload.wikimedia.org/wikipedia/commons/2/21/DNA_human_male_chromosomes.gif)
>
> Figure 1: A karyotype of a human male with a normal chromosome configuration.

> | hg38 chromosome | length    |
> |-----------------|-----------|
> | chr1            | 248956422 |
> | chr2            | 242193529 |
> | chr3            | 198295559 |
> | chr4            | 190214555 |
> | chr5            | 181538259 |
> | chr6            | 170805979 |
> | chr7            | 159345973 |
> | chr8            | 145138636 |
> | chr9            | 138394717 |
> | chr10           | 133797422 |
> | chr11           | 135086622 |
> | chr12           | 133275309 |
> | chr13           | 114364328 |
> | chr14           | 107043718 |
> | chr15           | 101991189 |
> | chr16           | 90338345  |
> | chr17           | 83257441  |
> | chr18           | 80373285  |
> | chr19           | 58617616  |
> | chr20           | 64444167  |
> | chr21           | 46709983  |
> | chr22           | 50818468  |
> | chrX            | 156040895 |
> | chrY            | 57227415  |
> 
> Table 1: `hg38` reference genome chromosome lengths.

It's worth noting that the nuclear genome, i.e., what is described above, is not the only genome in human cells.
Humans also have [mitochrondria](https://en.wikipedia.org/wiki/Mitochondrion), which have their own circular genome. 
This genome, sometimes represented as `chrMT` in reference genome files, is 16569 bp long in humans.


## File representation of reference genomes

Reference genomes are usually represented using the [FASTA file format](https://en.wikipedia.org/wiki/FASTA_format).

Our own [Bento reference service](https://github.com/bento-platform/bento_reference_service) ingests FASTA files, and
does all operations using the FASTA format + an index file.


## Common reference genomes

Here are some common reference genomes, and which Bento projects use them.

### Human

* `CHM13v2.0`: The "latest and greatest"; a more contiguous reference with several gaps filled in. This genome will be
  used in more projects going forward.
* `hg38`/`GRCh38`: 
  * BQC19: The CVMFS version on Alliance clusters at 
    `/cvmfs/soft.mugqic/CentOS6/genomes/species/Homo_sapiens.GRCh38/genome/Homo_sapiens.GRCh38.fa`
* `hg19`/`GRCh37`/`hs37d5`:
  * ICHANGE: The special `hs37d5` version derived from `GRCh37` is the 1000 Genomes Phase 2 reference genome.
    It is on Alliance clusters at 
    `/lustre03/project/6007512/C3G/analyste_dev/genomes/species/Homo_sapiens.hs37d5/genome/Homo_sapiens.hs37d5.fa`.

### Mouse

* `mm10`/`GRCm38`: an older mouse (*Mus musculus*) reference genome.
  * ICHANGE: The CVMFS version on Alliance clusters at 
    `/cvmfs/soft.mugqic/CentOS6/genomes/species/Mus_musculus.GRCm38/genome/Mus_musculus.GRCm38.fa` 

### Polar bear

* `UrsMar_1.0`: Used by BearWatch; available from https://www.ncbi.nlm.nih.gov/assembly/GCF_000687225.1/.


## Aspects to pay attention to!

* There can be many different versions of the same base reference genome - for example, ICHANGE specifically uses the
  `hs37d5` version of `GRCh37`, which **DOES NOT** have `chr` prefixes for the chromosomes, i.e., chromosome 1 is 
  represented as `1` instead of `chr1`. It is important to check which specific version is used!
  
  VCFs can be queried to find evidence for which reference genome was used:

  ```bash
  bcftools view -h ./path/to/the.vcf.gz
  ```
