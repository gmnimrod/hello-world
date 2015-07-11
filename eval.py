import sys
import getopt
from math import log10, pow
from stats import *
from helper_funcs import *

#### globals ####

metadata = {}                                           
stats_dicts = []                                        # holds statistics for each unique igram seen in text
igram_counts = []                                       # counter of total num of igrams seen (includes duplicates) 
test_print = False                                      # print for testing

#### functions ####

def process_model_file(model_filename):
    init_dicts(stats_dicts, igram_counts)
    f = open(model_filename, "r", encoding=default_encoding)
    lines = f.readlines()
    f.close()
    i = 1
    i = get_metadata(i, lines)
    i = get_ngram_counts(i, lines)
    while (i < len(lines)):
        i = get_stats(i, lines)
    if test_print:
        print (metadata)
        print (igram_counts)

def get_stats(i,lines):
    curr_ngram = int(lines[i][1])
    i+=1
    while (lines[i]!="\n" and i<len(lines)):
        tmp = lines[i].rstrip().split("\t")
        key = tmp[0]
        val = tmp[1:]
        stats_dicts[curr_ngram][key] = Stats(key.split(" ")[:-1])
        stats_dicts[curr_ngram][key].rebuild_stats(val[0], val[1],val[2])
        i+=1
    i+=1
    return  i


def get_metadata(i, lines):
    metadata.clear()
    while (lines[i]!="\\DATA\\\n"):         
        if lines[i]=="\n":
            pass
        else:
            key,val = lines[i].rstrip().split(":")
            if key.startswith("LAMBDA"):
                metadata[key] = float(val)
            elif key == "TYPE":
                metadata[key] = val
            else:
                metadata[key] = int(val)
        i+=1
    i+=1
    return i


def get_ngram_counts(i, lines):    
    while not (lines[i].endswith(":\n")):
        if lines[i] != "\n":
            key,val = lines[i].rstrip().split(" ")[1].split("=")
            igram_counts[int(key)] = int(val)
        i+=1
    return i


def process_test_file(test_filename):
    n = metadata["N"]
    f = open(test_filename, "r", encoding=default_encoding)
    perplexity_total_sum = 0 #for entire test file not just single sentence
    lines = 0
    for line in f:
        lines += 1
        tmp = fix_line(line)
        #tmp = map_unknown(tmp, stats_dicts)
        prob = 0
        for i in range(1,len(tmp) + 1):
            if i > n:
                prob += calc_prob(tmp[i-n:i])
            else:
                prob += calc_prob(tmp[:i])
        not_log_prob = pow(10, prob)
        if not_log_prob == 0.0: # occurs only when calculating extremely long sentences
            line_perplexity = 1 / epsilon
        else:
            line_perplexity = pow(not_log_prob, (-1/len(tmp)))
        perplexity_total_sum += line_perplexity
    perplexity_rank = perplexity_total_sum / lines
    print(perplexity_rank)
    f.close()
    return perplexity_rank


def calc_prob(expr_list):
    if metadata["TYPE"] == "wb":
        return calc_wb_interpolation(expr_list)
    expr = " ".join(expr_list)
    if (expr in stats_dicts[len(expr_list)].keys()):
        return stats_dicts[len(expr_list)][expr].Prob
    #unseen   
    if metadata["TYPE"] == "ls":
       return calc_lidstone_unseen(expr_list)
    #else - no smoothing- prob is 0
    return log10(epsilon)

def calc_lidstone_unseen(expr_list):
    without_last = " ".join(expr_list[:-1]) #empty if expr is a unigram  
    if metadata["LAMBDA"] == 0.0:
            return log10(epsilon)
    if (not without_last_exists(expr_list, without_last)):
        return log10(1/metadata["VOCABULARY"])      #lambda/(lambda*V)
    else:
        without_last_count = stats_dicts[len(expr_list[:-1])][without_last].Count
        return log10(metadata["LAMBDA"]/(without_last_count + (metadata["LAMBDA"]*metadata["VOCABULARY"])))

def calc_wb_interpolation(expr_list):
    prob = 0
    for i in range(1,len(expr_list)+1):
        prob += metadata["LAMBDA" + str(i)] * calc_wb_prob(expr_list[-i:])
    if prob > 1.0:
        print("SDFSDFSDF")
    if prob == 0.0:
        return log10(epsilon)
    return log10(prob)
        
def calc_wb_prob(expr_list):
    expr = " ".join(expr_list)
    without_last = " ".join(expr_list[:-1]) #empty if expr is a unigram  
    #all seen
    if (expr in stats_dicts[len(expr_list)].keys()):
        return pow(10,stats_dicts[len(expr_list)][expr].Prob)
    #just without_last seen
    if without_last_exists(expr_list, without_last):
        return pow(10, stats_dicts[len(expr_list[:-1])][without_last].Prob_wb_unseen)
    #nothing seen
    return 0.0

def without_last_exists(expr_list, without_last):
    return (without_last != '' and without_last in stats_dicts[len(expr_list)-1].keys())

def __main__(argv):
    model_filename = " "
    test_filename = " "
    try:
        opts, args = getopt.getopt(argv,"i:m:")
    except getopt.GetoptError:
        print("eval -i <input file> -m <model file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-i":
            test_filename = arg
        if opt == "-m":
            model_filename = arg

    process_model_file(model_filename)
    process_test_file(test_filename)
    return 1





if __name__ == "__main__":
    __main__(sys.argv[1:])














        
        
            
