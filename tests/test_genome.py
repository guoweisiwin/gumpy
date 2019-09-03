import pytest, numpy, copy

from pathlib import Path

from gumpy import Genome

TEST_CASE_DIR = "tests/test-cases/"

reference=Genome(genbank_file="config/NC_004148.2.gbk",name="HMPV")

def test_Genome_instantiate_genbank():

    # check that the M. tuberculosis H37rV genome is the right length
    assert reference.genome_length==13335

    # check the species is stored correctly
    assert reference.organism=='Human metapneumovirus'

    # check that the sequence starts and ends as we expect
    assert reference.genome_coding_strand[0]=='a'
    assert reference.genome_coding_strand[-1]=='t'

    assert len(reference.gene_names)==8

    # try a normal gene
    mask=reference.genome_feature_name=="M2"

    sequence=reference.genome_coding_strand[mask]
    first_codon="".join(i for i in sequence[:3])
    assert first_codon=="tta"
    last_codon="".join(i for i in sequence[-3:])
    assert last_codon=="tag"

    sequence=reference.genome_noncoding_strand[mask]
    first_codon="".join(i for i in sequence[:3])
    assert first_codon=="aat"
    last_codon="".join(i for i in sequence[-3:])
    assert last_codon=="atc"

    sequence=reference.genome_sequence[mask]
    first_codon="".join(i for i in sequence[:3])
    assert first_codon=="tta"
    last_codon="".join(i for i in sequence[-3:])
    assert last_codon=="tag"

reference2=Genome(fasta_file="config/NC_004148.2.fasta.gz",name="HMPV")

def test_Genome_instantiate_fasta():

    # check that the M. tuberculosis H37rV genome is the right length
    assert reference2.genome_length==13335

    # check the species is stored correctly
    assert reference2.organism=='Human metapneumovirus'

    # check that the sequence starts and ends as we expect
    assert reference2.genome_coding_strand[0]=='a'
    assert reference2.genome_coding_strand[-1]=='t'


def test_Genome_valid_gene_mutation_snps():

    # correct protein SNPs
    assert reference.valid_gene_mutation("F_M1N")
    assert reference.valid_gene_mutation("F_S2?")
    assert reference.valid_gene_mutation("F_S2=")
    assert reference.valid_gene_mutation("F_S2!")
    assert reference.valid_gene_mutation("M2_T76L")
    assert reference.valid_gene_mutation("M2_*?")
    assert reference.valid_gene_mutation("M2_-*?")

    with pytest.raises(Exception):

        # just badly formed
        assert reference.valid_gene_mutation("____")
        assert reference.valid_gene_mutation("")
        assert reference.valid_gene_mutation("flkgjslkjg")
        assert reference.valid_gene_mutation("o_o_o_o_9")
        assert reference.valid_gene_mutation("o_i9k")

        # genes not present
        assert reference.valid_gene_mutation("lkdfjlksdjf_P1N")
        assert reference.valid_gene_mutation("rpoB_P76L")

        # incorrect reference amino acids
        assert reference.valid_gene_mutation("F_P1N")
        assert reference.valid_gene_mutation("M2_P76L")

        # bad reference amino acids
        assert reference.valid_gene_mutation("F_;1N")
        assert reference.valid_gene_mutation("F_B1N")
        assert reference.valid_gene_mutation("F_81N")
        assert reference.valid_gene_mutation("M2_J76L")

        # bad positions
        assert reference.valid_gene_mutation("F_PKN")
        assert reference.valid_gene_mutation("F_P-2N")
        assert reference.valid_gene_mutation("F_P1000N")
        assert reference.valid_gene_mutation("F_P:N")

        # bad target amino acids
        assert reference.valid_gene_mutation("F_P1O")
        assert reference.valid_gene_mutation("F_PKB")
        assert reference.valid_gene_mutation("F_PK;")
        assert reference.valid_gene_mutation("F_PKJ")


def test_Genome_valid_gene_mutation_indels():

    # correct INDELs with good grammar
    assert reference.valid_gene_mutation("F_1_indel")
    assert reference.valid_gene_mutation("F_1_ins")
    assert reference.valid_gene_mutation("F_1_del")
    assert reference.valid_gene_mutation("F_1_ins_3")
    assert reference.valid_gene_mutation("F_1_ins_ctga")
    assert reference.valid_gene_mutation("F_1_fs")

    with pytest.raises(Exception):

        # bad grammar
        assert reference.valid_gene_mutation("F_1_indl")
        assert reference.valid_gene_mutation("F_1_frameshift")
        assert reference.valid_gene_mutation("F_1_del_3")
        assert reference.valid_gene_mutation("F_1_del_acgt")
        assert reference.valid_gene_mutation("F_1_ins_ggaf")

        # wrong ordering
        assert reference.valid_gene_mutation("F_indel_1")

        # incorrect gene
        assert reference.valid_gene_mutation("F1_1_indel")

        # in promoter
        assert reference.valid_gene_mutation("F_-1_indel")

        # not in gene
        assert reference.valid_gene_mutation("F_1000_indel")

def test_Genome_valid_genome_variant():

    assert reference.valid_genome_variant("a1c")
    assert reference.valid_genome_variant("c2g")
    assert reference.valid_genome_variant("g3a")
    assert reference.valid_genome_variant("t13335g")

    with pytest.raises(Exception):

        # incorrect reference base
        assert reference.valid_genome_variant("t1c")
        assert reference.valid_genome_variant("a2g")
        assert reference.valid_genome_variant("t3a")
        assert reference.valid_genome_variant("c13335g")

        # badly formed reference base
        assert reference.valid_genome_variant("11c")
        assert reference.valid_genome_variant("?2g")
        assert reference.valid_genome_variant("P3a")
        assert reference.valid_genome_variant(" 13335g")

        # out of range index
        assert reference.valid_genome_variant("a0c")
        assert reference.valid_genome_variant("c-1g")
        assert reference.valid_genome_variant("g-2a")
        assert reference.valid_genome_variant("t13336g")

        # badly formed index
        assert reference.valid_genome_variant("a1.1c")
        assert reference.valid_genome_variant("c2fg")
        assert reference.valid_genome_variant("gya")
        assert reference.valid_genome_variant("tg")

def test_Genome_gbk_fasta_identical():

    assert reference.genome_length==reference2.genome_length

    assert numpy.array_equal(reference.genome_coding_strand,reference2.genome_coding_strand)

    assert numpy.array_equal(reference.genome_index,reference2.genome_index)


def test_Genome___repr__():

    assert reference.__repr__()=='NC_004148.2\nHuman metapneumovirus\nHMPV\n13335 bases\nacg...cgt'


def test_Genome___sub__():

    sample=copy.deepcopy(reference)

    sample.genome_coding_strand[2]='t' # remember that the genome is 1-based, but the numpy array is 0-based

    indices=reference-sample

    assert indices[0]==3

    assert sample.genome_coding_strand[2]=='t'

def test_Genome_contains_gene():

    assert reference.contains_gene("F")==True
    assert reference.contains_gene("FG")==False
    assert reference.contains_gene(5)==False
    assert reference.contains_gene("")==False
    assert reference.contains_gene("rpoBC")==False
    assert reference.contains_gene("RPOB")==False

def test_Genome_at_index():

    assert reference.at_index(4686)=='F'
    assert reference.at_index(4687)=='M2'
    assert reference.at_index(5293)=='M2'
    assert reference.at_index(5450)=='M2'
    assert reference.at_index(5451)=='SH'
    assert reference.at_index(7032) is None
    assert reference.at_index(7033)=="L"
    assert reference.at_index(13150)=="L"
    assert reference.at_index(13151) is None

    # wrong gene
    assert reference.at_index(7033)!="F"
    assert reference.at_index(7033) is not None

    with pytest.raises(Exception):

        # bad position
        reference.at_index(-2)
        reference.at_index(0)
        reference.at_index(1.3)
        reference.at_index('gh')
        reference.at_index(13336)

def test_Genome_calculate_snp_distance():

    sample=copy.deepcopy(reference)

    sample.genome_coding_strand[2]='t' # remember that the genome is 1-based, but the numpy array is 0-based
    assert sample.snp_distance(reference)==1

    # reverse the change
    sample.genome_coding_strand[2]='g'
    assert sample.snp_distance(reference)==0

    # now change two bases
    sample.genome_coding_strand[2]='t'
    sample.genome_coding_strand[3]='t'
    assert sample.snp_distance(reference)==2

sample_01=copy.deepcopy(reference)
sample_01.apply_vcf_file(vcf_file=TEST_CASE_DIR+"01.vcf",ignore_status=True,ignore_filter=True,metadata_fields=['GT_CONF','GT_CONF_PERCENTILE'])

def test_Genome_apply_vcf():

    indices=reference-sample_01
    assert indices[0]==4687
    assert reference.genome_coding_strand[reference.genome_index==indices[0]]=='t'
    assert sample_01.genome_coding_strand[reference.genome_index==indices[0]]=='c'
    assert sample_01.coverage[sample_01.genome_index==4687]==68
    assert sample_01.genome_sequence_metadata['GT_CONF'][sample_01.genome_index==4687][0]==pytest.approx(613.77)

def test_Genome_list_variants_wrt():

    assert sample_01.list_variants_wrt(reference)==['t4687c']


def test_Genome__complement():
    
    test_sequence=numpy.array(['a','c','t','g','z','x'])

    assert numpy.array_equal(reference._complement(test_sequence),numpy.array(['t','g','a','c','z','x']))

    # sample_04=copy.deepcopy(reference)
    # sample_04.apply_vcf_file(vcf_file=TEST_CASE_DIR+"04.vcf",ignore_status=True,ignore_filter=True,metadata_fields=['GT_CONF'])
    # (original_bases,indices,new_bases)=reference-sample_04
    # assert original_bases[0]=='c'
    # assert indices[0]==2155168
    # assert new_bases[0]=='g'
    # assert sample_04.coverage[sample_04.index==2155168]==53
    # assert sample_04.sequence_metadata['GT_CONF'][sample_04.index==2155168][0]==pytest.approx(500.23)
