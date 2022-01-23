import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--square", type=int, help="display a square of a given number")
args = parser.parse_args()
print(args)
print(args.square)
