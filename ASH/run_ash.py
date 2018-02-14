#----------------------------------------------------------------------#
#               Antigen Selection Heuristic {ASH}                      #
#----------------------------------------------------------------------#
#                                                                      #
#                  Written by Thadryan J. Sweeney                      #
#                      with Python 3.5.3                               #
#                           2/13/18                                    #
#                                                                      #
#                     Usage Dependencies:                              #
#                        -Python 3.5.3                                 #
#                        -Scikit-bio                                   #
#                                                                      #
# This program analyzes FASTA sequences to find regions of chemical    #
# distinctness and antigenicty. It takes in two fasta files, a name    #
# for an output file,and a desired Kmer length via the command line.   #
# It scores them on a simple hydrophilicity-based scale developed for  #
# this script. More on the thought process behind the ASH scale can be #
# foond on the ASH github. It also implements a simple hydrophilicity  #
# -based antigenicty metric that is currently under development at the #
# time of tis writing (2/13/18). The intent is that this tool can help #
# users analyze protein sequence for epitope/antigen selection by      #
# automating the search for eptitopes that are distinct to their       #
# protein or, conversly, find regions that are well conserved in       #
# both. The output is a csv file containing information on all the     #
# eptitopes in the first protein, it's ASH score, it's index in the    #
# sequence, it's antigenicty rating, and the sequence it's analog in   #
# the second sequence.                                                 #
#----------------------------------------------------------------------#


import sys
from skbio.alignment import StripedSmithWaterman


class analyze(object):
#----------------------------------------------------------------------#
#                            constructor                               #
#----------------------------------------------------------------------#
# The constructor takes 3 arguments: two .fasta files and an integer   #
# of the desired kmer length. It calls functions to get the sequences  #
# out of the files(get_seq), align the sequences (align), compare them #
# using the scale(seq_to_seq), and writes the data to a csv            #
#----------------------------------------------------------------------#
    def __init__(self, first_seq_in, second_seq_in, outfile, kmer):
        # the kmer size
        self.kmer_size    = kmer
        # get the two sequences
        self.first_fasta  = self.get_seq(first_seq_in)
        self.second_fasta = self.get_seq(second_seq_in)
        # call the skikit bio alignmnt function
        self.aligned      = self.align(self.first_fasta,
                                       self.second_fasta)
        # get the two sequences from the alignment
        self.sequence1    = self.aligned[0]
        self.sequence2    = self.aligned[1]
        # implement the ASH proceedure on the two sequences
        self.results      = self.seq_to_seq(self.sequence1,
                                            self.sequence2,
                                            self.kmer_size)
        # get name for outfile
        self.outname      = outfile
        # write the output to a csv file
        self.output       = self.report(self.results)


#----------------------------------------------------------------------#
#                          Entry(class)                                #
#----------------------------------------------------------------------#
# This is a nested class to store the results of the analysis. I opted #
# to nest the class to compartmentalize the code and because the ASH   #
# class is the only class that uses the entry class. It holds the      #
# sequence, it's position, it's ASH and antigenicty scores, and the    #
# sequence that it was compared to. Enties are created by the seq_to_  #
# seq function. The results of this script is a list of Entry objects  #                              #
#----------------------------------------------------------------------#
    class Entry(object):
        # arguments are passed to the contructor by the seq_to_seq function
        def __init__(self, seq, pos, score, match, antg):
            self.seq   =   seq   # the peptide
            self.pos   =   pos   # what index is appears
            self.score = score   # the mismatch score
            self.match = match   # what it was compared to
            self.antg  = antg    # the simple antigenicty score


#----------------------------------------------------------------------#
#                            get_seq                                   #
#----------------------------------------------------------------------#
# This is a vanilla fasta parser for solo fasta files. Skips header,   #
# strips newlines, and concatenates sequences. Returns sequence        #
#----------------------------------------------------------------------#
    def get_seq(self, filename):
        # will store the sequence
        seq = ""
        # bail if file is not valid
        data = open(filename, "r").readlines()
        # get the sequence
        for line in data:
            if not line.startswith(">"):      # skips header
                line = line.replace("\n", "") # removes newlines
                seq += line
        return seq


#----------------------------------------------------------------------#
#                               align                                  #
#----------------------------------------------------------------------#
# Takes the parsed fasta files from get_seq (called by contructor) and #
# passes them to scikit bio's StripedSmithWaterman function. Returns   #
# an array with the sequences. We need to access the sequences         #
# individually now that the gaps have been filled in appropiately      #
#----------------------------------------------------------------------#
    def align(self, seq1, seq2):
        # store sequences
        aligned_seqs = []
        # make initial query
        query = StripedSmithWaterman(seq1)
        # align second seq against initial query
        align = query(seq2)
        # add individual sequences to results
        aligned_seqs.append(align.aligned_query_sequence)
        aligned_seqs.append(align.aligned_target_sequence)
        return aligned_seqs


#----------------------------------------------------------------------#
#                         weighted_score                               #
#----------------------------------------------------------------------#
# This implements the scale on a pair of residues. It is called by the #
# mismatch function to score pairs of peptides at an index             #
#----------------------------------------------------------------------#
    def weighted_score(self, residue1, residue2):
        # hydrophiles are positive, hydrophobic is negative, neutral is 0
        weight = {  "L":-0.5, "A":-0.5, "F":-0.5, "Y":-0.5, "W":-0.5,
                    "I":-0.5, "V":-0.5, "H":+0.0, "N":+0.0, "C":+0.0,
                    "G":+0.0, "M":+0.0, "Q":+0.0, "P":+0.0, "S":+0.0,
                    "T":+0.0, "D":+0.5, "E":+0.5, "R":+0.5, "K":+0.5 }
        # a gap is given a score of two in our system
        if residue1 == "-" or residue2 == "-":
            return 2.0
        # subscore is the abs value of the scores
        subscore = abs(weight[residue1] - weight[residue2])
        # same group returns 0.25
        if subscore == 0:
            return 0.25
        else:
            return subscore


#----------------------------------------------------------------------#
#                              mismatch                                #
#----------------------------------------------------------------------#
# This takes two kmers and iterates through them. It calls the         #
# weighted_score function on the two residues at each index and        #
# returns the total "mismatch" score for the kmer                      #
#----------------------------------------------------------------------#
    def mismatch(self, input_seq1, input_seq2):
        score = 0
        # iterate through length
        for i in range(len(input_seq1)):
            # excact match == no mismatch score
            if input_seq1[i] == input_seq2[i]:
                score += 0
            else:
                # call the weighted_score score method
                score += self.weighted_score(input_seq1[i], input_seq2[i])
        return score


#----------------------------------------------------------------------#
#                            antigenicity                              #
#----------------------------------------------------------------------#
# This function takes a simple measure of antigenicty based on the     #
# percent of residues that are hydrophiles                             #
#----------------------------------------------------------------------#
    def antigenicity(self, seq):
        simple_scores = ["D","E","R","K"]
        score = 0
        for item in seq:
            if item in simple_scores:
                score += 1
        return round(score/len(seq), 2)


#----------------------------------------------------------------------#
#                            seq_to_seq                                #
#----------------------------------------------------------------------#
# This function is the driver of the tool. It acts on the whole        #
# protein sequence of the files entered into the contructor. It also   #
# takes the kmer length argument. It iterates through the whole        #
# of both sequences in steps equal to the kmer size. It asses the two  #
# kmers at that region in both proteins, and scores them. It builds an #
# Entry object for each kmer, and returns a list of Entry objects      #
#----------------------------------------------------------------------#
    def seq_to_seq(self, seq1, seq2, length):
        # to store Entry objects
        results = []
        # start at zero
        position = 0
        # while move along the sequence won't put us over the edge
        while position + length <= len(seq1):
            # the current_peptide is the kmer is seq one, it
            # starts at the currrent position, ends at position + kmer length
            current_peptide = seq1[position:position+length]
            compare_peptide = seq2[position:position+length]
            # call mismatch on the current kmers
            entry = self.mismatch(current_peptide, compare_peptide)
            # store results is an Entry object
            results_obj = self.Entry(
                seq   = current_peptide,
                pos   = position,
                score = entry,
                match = compare_peptide,
                antg  = self.antigenicity(current_peptide))
            # store objects, increment counter
            results.append(results_obj)
            position += 1
        return results


#----------------------------------------------------------------------#
#                              report                                  #
#----------------------------------------------------------------------#
# Writes a csv file with the stats of each object as a row             #
#----------------------------------------------------------------------#
    def report(self, records):
        outfile = open(self.outname + ".csv", "w")
        outfile.write("index,sequence,ash_score,antigenicty,analog_sequence\n")
        for item in records:
            outfile.write(str(item.pos)   + "," +
                          item.seq        + "," +
                          str(item.score) + "," +
                          str(item.antg)  + "," +
                          item.match      + "\n")

        outfile.close()


#----------------------------------------------------------------------#
#                         __main script__                              #
#----------------------------------------------------------------------#
# Gets argv, handles exceptions, executes the program                  #
#----------------------------------------------------------------------#

# get the first fasta
first_seq_in  = sys.argv[1]
# get the second fasta
second_seq_in = sys.argv[2]
# get name for outfile
outfile_name  = sys.argv[3]

# do we have the corrct number of arguments? ball if false
if len(sys.argv) != 5:
    sys.exit("Incorrect number of arguments.")

# handle first file
try:
    test_file_one = open(first_seq_in, "r")
except FileNotFoundError:
    sys.exit("First file is invald.")
test_file_one.close()

# handle second file
try:
    test_file_two = open(second_seq_in, "r")
except FileNotFoundError:
    sys.exit("Second file is invald.")
test_file_two.close()

# is kmer a number? bail is false
try:
    kmer_arg      = int(sys.argv[4])
except ValueError:
    sys.exit("Please enter and integer for kmer length")

# create ash analyze object if everything is in order.
main = analyze(first_seq_in, second_seq_in, outfile_name, kmer_arg)
