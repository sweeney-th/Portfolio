import sys

# add to path so tests can be run from home directory
sys.path.append(".")
from ASH import Analysis

test_obj = Analysis("test/test1.fasta", "test/test2.fasta", 15)



""" testing get seq """

def test_get_seq_first():
    print("testing get_seq, first sequence")
    assert(test_obj.first_fasta == "MRVKGIRRNYQHWWGWGTMLLGLLMICSATEKLWVTVYYGVPVWKEATTTLFCASDAKAY")

def test_get_seq_second():
    print("testing get_seq, second sequence")
    assert(test_obj.second_fasta == "MRVRGMQRNWQHLGKWGLLFLGILIICNAADNLWVTVYYGVPVWKEATTTLFCASDAKAY")



### hydro_precent
def test_hydro_percent_positive():
    assert(test_obj.hydro_percent("DDDDD") == 1)

def test_hydro_percent_positive_mixed():
    assert(test_obj.hydro_percent("DDGD") == 0.75)

def test_hydro_percent_negative():
    assert(test_obj.hydro_percent("LLLLL") == 0)

def test_hydro_percent_negative_mixed():
    assert(test_obj.hydro_percent("LLLG") == 0)


""" hydro_score """

# test residue vs underscore
def test_hydro_score_on_underscore():
    # highest distance is a residue to a gap
    assert(test_obj.hydro_score("A", "-") == 2)

# gap to gap should be no penalty
def test_hydro_two_underscores():
    assert(test_obj.hydro_score("-", "-") == 0)

# test phile to no-identical phile
def test_hydro_score_on_same_group_phile():
    assert(test_obj.hydro_score("D", "E") == 0.25)

# test on identical
def test_hydro_score_on_identical_residue():
    assert(test_obj.hydro_score("D", "D") == 0)

# test phobe vs phobe
def test_hydro_score_on_same_group_phobe():
    assert(test_obj.hydro_score("L", "Y") == 0.25)

# test on phile vs phobe
def test_hydro_score_on_opposite():
    assert(test_obj.hydro_score("D", "Y") == 1)

# a hydrophile vs a neutral residue
def test_phile_vs_neutral():
    assert(test_obj.hydro_score("D", "H") == 0.5)

# a hydrophobe vs a neutral residue
def test_phile_vs_neutral():
    assert(test_obj.hydro_score("L", "H") == 0.5)

# a neutral vs a neutral residue
def test_phile_vs_neutral():
    assert(test_obj.hydro_score("T", "H") == 0.25)



""" hydro_mismatch """

# test simple phile vs phobe
def test_mismatch_phile_v_phobe():
    assert(test_obj.hydro_mismatch("DD", "LL") == 2.0)

# test simple phile vs neutral
def test_mismatch_phile_v_neutral():
    assert(test_obj.hydro_mismatch("DD", "HH") == 1.0)

# test simple phobe vs neutral
def test_mismatch_phobe_v_neutral():
    assert(test_obj.hydro_mismatch("LL", "HH") == 1.0)

def test_mismatch_on_simple_peptides():
    assert(test_obj.hydro_mismatch("PEPTIDE", "PEPTYDE") == 0.25)

def test_mismatch_on_peptides_with_gap():
    assert(test_obj.hydro_mismatch("PEPT-DE", "PEPTYDE") == 2.0)

def test_mismatch_on_peptides_with_two_gaps():
    assert(test_obj.hydro_mismatch("PEPT-DE", "PEPT-DE") == 0)



""" structure_score """

# does a mismatch get noticed?
def test_struct_score_miss():
    assert(test_obj.structural_mismatch("A", "Y") == 1)

# does a match get ignored?
def test_struct_score_hit_match():
    assert(test_obj.structural_mismatch("F", "F") == 0)

# does a similar residue get less weight?
def test_struct_score_non_match():
    assert(test_obj.structural_mismatch("F", "H") == 0.5)
