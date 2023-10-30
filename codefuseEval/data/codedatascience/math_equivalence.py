import os
import pickle
from test_code import *
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--test_case", type=int, default=1)
args = parser.parse_args()
with open( os.getcwd() + "/ans/ans" + str(args.test_case) + ".pkl", "rb" ) as res:
    ref = pickle.load( res )
with open( "result/result_{}.pkl".format( str(args.test_case) ), "rb" ) as answer:
    ans = pickle.load( answer )

assert 1 == test(ans,ref)
