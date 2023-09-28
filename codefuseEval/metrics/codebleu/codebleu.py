# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

# -*- coding:utf-8 -*-
import metrics.codebleu.bleu as bleu
import metrics.codebleu.weighted_ngram_match as weighted_ngram_match
import metrics.codebleu.syntax_match as syntax_match
import metrics.codebleu.dataflow_match as dataflow_match
import os
import json


class CodeBleu():
    def compute(self, predictions, references, lang="java", params="0.25,0.25,0.25,0.25"):
        alpha, beta, gamma, theta = [float( x ) for x in params.split( ',' )]

        # preprocess inputs
        hypothesis = [x.strip() for x in predictions]

        assert isinstance( references, list )
        assert all( [isinstance( reference, str ) for reference in references] ) or (all( [isinstance( reference, list ) for reference in references] ) and all( [all( [isinstance( x, str ) for x in reference] ) for reference in references] ))

        if all( [isinstance( reference, str ) for reference in references] ):
            pre_references = [[x.strip() for x in references]]
        if (all( [isinstance( reference, list ) for reference in references] ) and all( [all( [isinstance( x, str ) for x in reference] ) for reference in references] )):
            pre_references = [[x.strip() for x in reference] for reference in references]

        for i in range( len( pre_references ) ):
            assert len( hypothesis ) == len( pre_references[i] )

        references = []
        for i in range( len( hypothesis ) ):
            ref_for_instance = []
            for j in range( len( pre_references ) ):
                ref_for_instance.append( pre_references[j][i] )
            references.append( ref_for_instance )
        assert len( references ) == len( pre_references ) * len( hypothesis )

        # calculate ngram match (BLEU)
        tokenized_hyps = [x.split() for x in hypothesis]
        tokenized_refs = [[x.split() for x in reference] for reference in references]

        ngram_match_score = bleu.corpus_bleu( tokenized_refs, tokenized_hyps )

        # calculate weighted ngram match
        path = os.path.dirname( __file__ )
        keywords = [x.strip() for x in open( path + os.sep + 'keywords/' + lang + '.txt', 'r', encoding='utf-8' ).readlines()]

        def make_weights(reference_tokens, key_word_list):
            return {token: 1 if token in key_word_list else 0.2 \
                    for token in reference_tokens}

        tokenized_refs_with_weights = [[[reference_tokens, make_weights( reference_tokens, keywords )] \
                                        for reference_tokens in reference] for reference in tokenized_refs]

        weighted_ngram_match_score = weighted_ngram_match.corpus_bleu( tokenized_refs_with_weights, tokenized_hyps )

        # calculate syntax match
        syntax_match_score = syntax_match.corpus_syntax_match( references, hypothesis, lang )

        # calculate dataflow match
        dataflow_match_score = dataflow_match.corpus_dataflow_match( references, hypothesis, lang )

        print( 'ngram match: {0}, weighted ngram match: {1}, syntax_match: {2}, dataflow_match: {3}'. \
               format( ngram_match_score, weighted_ngram_match_score, syntax_match_score, dataflow_match_score ) )

        code_bleu_score = alpha * ngram_match_score \
                          + beta * weighted_ngram_match_score \
                          + gamma * syntax_match_score \
                          + theta * dataflow_match_score

        print( 'CodeBLEU score: ', code_bleu_score )
        return {"ngram match": ngram_match_score, "weighted ngram match": weighted_ngram_match_score, "syntax_match": syntax_match_score, "dataflow_match": dataflow_match_score, "CodeBLEU_Score": code_bleu_score}



def compute_codebleu(predictions, references, lang="java", params="0.25,0.25,0.25,0.25"):
    alpha, beta, gamma, theta = [float( x ) for x in params.split( ',' )]

    # preprocess inputs
    try:
        [x.strip() for x in predictions]
    except:
        print( predictions )
    hypothesis = [x.strip() for x in predictions]

    assert isinstance( references, list )
    assert all( [isinstance( reference, str ) for reference in references] ) or (all( [isinstance( reference, list ) for reference in references] ) and all( [all( [isinstance( x, str ) for x in reference] ) for reference in references] ))

    if all( [isinstance( reference, str ) for reference in references] ):
        pre_references = [[x.strip() for x in references]]
    if (all( [isinstance( reference, list ) for reference in references] ) and all( [all( [isinstance( x, str ) for x in reference] ) for reference in references] )):
        pre_references = [[x.strip() for x in reference] for reference in references]

    for i in range( len( pre_references ) ):
        assert len( hypothesis ) == len( pre_references[i] )

    references = []
    for i in range( len( hypothesis ) ):
        ref_for_instance = []
        for j in range( len( pre_references ) ):
            ref_for_instance.append( pre_references[j][i] )
        references.append( ref_for_instance )
    assert len( references ) == len( pre_references ) * len( hypothesis )

    # calculate ngram match (BLEU)
    tokenized_hyps = [x.split() for x in hypothesis]
    tokenized_refs = [[x.split() for x in reference] for reference in references]

    ngram_match_score = bleu.corpus_bleu( tokenized_refs, tokenized_hyps )

    # calculate weighted ngram match
    path = os.sep.join( os.path.abspath( __file__ ).split( os.sep )[:-1] ) + os.sep
    keywords = [x.strip() for x in open( path + 'keywords/' + lang + '.txt', 'r', encoding='utf-8' ).readlines()]

    def make_weights(reference_tokens, key_word_list):
        return {token: 1 if token in key_word_list else 0.2 \
                for token in reference_tokens}

    tokenized_refs_with_weights = [[[reference_tokens, make_weights( reference_tokens, keywords )] \
                                    for reference_tokens in reference] for reference in tokenized_refs]

    weighted_ngram_match_score = weighted_ngram_match.corpus_bleu( tokenized_refs_with_weights, tokenized_hyps )

    # calculate syntax match
    syntax_match_score = syntax_match.corpus_syntax_match( references, hypothesis, lang )

    # calculate dataflow match
    dataflow_match_score = dataflow_match.corpus_dataflow_match( references, hypothesis, lang )

    print( 'ngram match: {0}, weighted ngram match: {1}, syntax_match: {2}, dataflow_match: {3}'. \
           format( ngram_match_score, weighted_ngram_match_score, syntax_match_score, dataflow_match_score ) )

    code_bleu_score = alpha * ngram_match_score \
                      + beta * weighted_ngram_match_score \
                      + gamma * syntax_match_score \
                      + theta * dataflow_match_score

    print( 'CodeBLEU score: ', code_bleu_score )
    return {"ngram match": ngram_match_score, "weighted ngram match": weighted_ngram_match_score, "syntax_match": syntax_match_score, "dataflow_match": dataflow_match_score, "CodeBLEU_Score": code_bleu_score}

# if __name__ == "__main__":
#
#     # python_prediction =["""def canWinNim(n: int) -> bool:\n	return n % 4 != 0"""]
#     # python_reference = ["""def canWinNim(n: int) -> bool:\n	if n <= 3:\n		return True\n	dp = [False] * (n+1)\n	dp[1] = dp[2] = dp[3] = True\n	for i in range(4, n+1):\n		dp[i] = not(dp[i-1] and dp[i-2] and dp[i-3])\n	return dp[n]\n"""]
#     # result = compute_codebleu(predictions = python_prediction,references = python_reference,lang="python")
#     f = open( "/ossfs/workspace/testcase_gpt4.jsonl", "r" )
#     dataset = f.readlines()
#     predictions = [json.loads( data )["miaozhen_answer"] for data in dataset]
#     predictions1 = [json.loads( data )["guanyi_answer"] for data in dataset]
#     predictions2 = [json.loads( data )["congan_answer"] for data in dataset]
#     references = [json.loads( data )["gpt4_answer"] for data in dataset]
#
#     import evaluate
#
#     bleurt = evaluate.load( "/ossfs/workspace/metrics/bleurt", config_name="bleurt-large-512" )
#     score_miaozhen = bleurt.compute( references=references, predictions=predictions )
#     score_guanyi = bleurt.compute( references=references, predictions=predictions1 )
#     score_congan = bleurt.compute( references=references, predictions=predictions2 )
#
#     miaozhen_scores = score_miaozhen["scores"]
#     guanyi_scores = score_guanyi["scores"]
#     congan_scores = score_congan["scores"]
#
#     miaozhen_codebleu_score = []
#     guanyi_codebleu_score = []
#     congan_codebleu_score = []
#
#     # print(compute_codebleu(predictions = predictions,references = references,lang="python"))
#     for prediction, reference in zip( predictions, references ):
#         result = compute_codebleu( predictions=[prediction], references=[reference], lang="python" )
#         miaozhen_codebleu_score.append( result )
#
#     for prediction, reference in zip( predictions1, references ):
#         result = compute_codebleu( predictions=[prediction], references=[reference], lang="python" )
#         guanyi_codebleu_score.append( result )
#
#     for prediction, reference in zip( predictions2, references ):
#         result = compute_codebleu( predictions=[prediction], references=[reference], lang="python" )
#         congan_codebleu_score.append( result )
#
#     final_result = []
#     for data, miaozhen_score, guanyi_score, congan_score, miaozhen_codebleu, guanyi_codebleu, congan_codebleu in zip( dataset, miaozhen_scores, guanyi_scores, congan_scores, miaozhen_codebleu_score, guanyi_codebleu_score, congan_codebleu_score ):
#         data = json.loads( data )
#         data["miaozhen_bleurt_score"] = miaozhen_score
#         data["guanyi_bleurt_score"] = guanyi_score
#         data["congan_bleurt_score"] = congan_score
#         data["miaozhen_codebleu_score"] = miaozhen_codebleu
#         data["guanyi_codebleu_score"] = guanyi_codebleu
#         data["congan_codebleu_score"] = congan_codebleu
#         final_result.append( json.dumps( data, ensure_ascii=False ) )
#
#     with open( "testcase_gpt4_result.jsonl", "w" ) as f:
#         f.write( "\n".join( final_result ) )
