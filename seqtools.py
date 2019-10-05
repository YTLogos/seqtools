# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 21:00:49 2019

@author: taoyan
"""

'''
This is a collection of python script for genome sequence analysis
'''

__author__      = "Tao Yan"
__version__     = "v1.0"
__email__       = "tyan@zju.edu.cn"
__date__        = "2019-09-05"


import sys
import os
import argparse
import gzip


def main():
    #argparse设置参数
    ##创建解析器
    parser=argparse.ArgumentParser(description="Some useful functions for dealing with genome data", formatter_class=argparse.RawDescriptionHelpFormatter)

    ##创建子命令
    sub_parser=parser.add_subparsers()

    ##添加子命令extract
    extract_parser=sub_parser.add_parser("extract", help="Extract sequence based sequence id \nUsage: python seqtools.py extract -i input.fasta (or input.fasta.gz) -l seq_id.txt -o output.fasta (or output.fasta.gz)")
    ###为命令extract添加参数
    extract_parser.add_argument("--input","-i", action="store", required=True, help="Name of the input file (.fasta or others), can be gzipped")
    extract_parser.add_argument("--seq_id_list","-l", action="store", required=True, help="The sequence id you want to extract (.txt)")
    extract_parser.add_argument("--output","-o", action="store", required=True, help="name of the output file (.fasta or others), can be gzipped")

    ##添加子命令sort
    sort_parser=sub_parser.add_parser("sort", help="Sort the sequence by sequence id or length \nUsage: python seqtools.py sort -i test.fasta (or test.fasta.gz) -by 'id (or len)' -o output.fasta (or output.fasta.gz)")
    ###为子命令sort添加参数
    sort_parser.add_argument("--input","-i", action="store", required=True, help="Name of the input file (.fasta or others), can be gzipped")
    sort_parser.add_argument("--sort_by","-by", type=str, help="Sort sequence by sequence id (id) or sequence length (len)")
    sort_parser.add_argument("--output","-o", action="store", required=True, help="name of the output file (.fasta or others), can be gzipped")
    ##是否需要反向排序，默认是不需要（按从小到大的顺序进行排序），如果需要的话，就需要指定参数-r（按从大到小的顺序进行排序）
    sort_parser.add_argument('--rev',"-r", action="store_true")

    ##添加子命令remove
    remove_parser=sub_parser.add_parser("remove", help="Remove the last character (i.e. *,.?...) of each line\nUsage: python seqtools.py remove -i test.pep (or test.pep.gz) -c '.' -o output.pep (output.pep.gz)")
    ###为子命令添加参数
    remove_parser.add_argument("--input","-i", action="store", required=True, help="Name of the input file (.fasta or others), can be gzipped")
    remove_parser.add_argument("--character","-c", type=str, help="the character need to be removed")
    remove_parser.add_argument("--output","-o", action="store", required=True, help="Name of the output file (.fasta or others), can be gzipped")

    ##添加子命令add_id2vcf
    add_id2vcf_parser=sub_parser.add_parser("add_id2vcf", help="Add id to the vcf file,ID=chromosome+position\nUsage: python seqtools.py add_id2vcf -i test.vcf (or test.vcf.gz) -o output.vcf (or output.vcf.gz)")

    ###为子命令add_id2vcf添加参数
    add_id2vcf_parser.add_argument("--input","-i", action="store", required=True, help="Name of the input file (.vcf), can be gzipped")
    add_id2vcf_parser.add_argument("--output","-o", action="store", required=True, help="Name of the output file (.vcf), can be gzipped")




    ##指定不同的子命令执行的函数
    ### 子命令extract执行定义的函数extract
    extract_parser.set_defaults(func=extract)
    ### 子命令sort执行定义的函数sort
    sort_parser.set_defaults(func=sort)
    ### 子命令remove执行定义的remove函数
    remove_parser.set_defaults(func=remove)
    ### 子命令add_id2vcf执行定义的add_id2vcf函数
    add_id2vcf_parser.set_defaults(func=add_id2vcf)

    ##解析参数
    args=parser.parse_args()
    args.func(args)


# Define the function to extract sequence by sequence id, you need offer a list(txt) with one row one seq_id
def extract(args):
    if args.output.endswith(".gz"):
        outputfile=gzip.open(args.output, "wt")
    else:
        outputfile=open(args.output, "w")
    fasta={}
    if args.input.endswith(".gz"):
        opener = gzip.open
    else:
        opener = open
    with opener(args.input,'rt') as inputfile:
        for line in inputfile:
            if line.startswith('>'):
                ID=line.strip().split()[0][1:]
                fasta[ID]=''
            else:
                fasta[ID]+=line
    with open (args.seq_id_list,"r") as listfile:
        for row in listfile:
            row=row.strip()
            for key in fasta.keys():
                if key == row:
                    outputfile.write(">"+key+"\n")
                    outputfile.write(fasta[key])
    outputfile.close()

## Define the function to sort the sequence by sequence id or sequence length
def sort(args):
    if args.output.endswith(".gz"):
        outputfile=gzip.open(args.output, "wt")
    else:
        outputfile=open(args.output, "w")
    fasta={}
    if args.input.endswith(".gz"):
        opener=gzip.open
    else:
        opener=open
    with opener(args.input,"rt") as inputfile:
        for line in inputfile:
            if line.startswith(">"):
                ID=line
                fasta[ID]=''
            else:
                fasta[ID]=fasta[ID]+line
        if args.sort_by=="id":
            fasta=sorted(fasta.items(), key=lambda i:i[0], reverse=args.rev)#按照序列id进行排序，需要反向排序的话，添加参数reverse=True,下同
        elif args.sort_by=="len":
            fasta=sorted(fasta.items(), key=lambda i:len(i[1]), reverse=args.rev)#按照序列长度进行排序
        else:
            fasta=fasta.items()
    for k,v in fasta:
        outputfile.write(k+v)
    outputfile.close()
    
    
## define the function to remove the last character of each line  
def remove(args):
    if args.output.endswith(".gz"):
        outputfile=gzip.open(args.output, "wt")
    else:
        outputfile=open(args.output, "w")
    if args.input.endswith(".gz"):
        opener=gzip.open
    else:
        opener=open
    with opener(args.input,"rt") as inputfile:
        for line in inputfile:
            line=line.strip()
            if not line.endswith(args.character):
                outputfile.write(line+'\n')
            else:
                line=line[:-1]
                outputfile.write(line+'\n')
    outputfile.close()

## define the function to add SNP id to vcf file
def add_id2vcf(args):
    if args.output.endswith(".gz"):
        outputfile=gzip.open(args.output, "wt")
    else:
        outputfile=open(args.output, "w")
    if args.input.endswith(".gz"):
        opener=gzip.open
    else:
        opener=open
    with opener(args.input,"rt") as vcffile:
        for line in vcffile:
            if line.startswith("#"):
                outputfile.write(line)
            else:
                l=line.strip("\n").split()
                l[2]=l[0]+"_"+l[1]
                f='	'.join(l)
                outputfile.write(f+"\n")
    outputfile.close()

if __name__=="__main__":
    main()
