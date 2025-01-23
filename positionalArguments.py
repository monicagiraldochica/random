import argparse

parser = argparse.ArgumentParser()
# If not specified, the type by default is string
parser.add_argument("arg1", help="Description of arg1")
parser.add_argument("arg2", help="This should be an integer and will be squared", type=int)
args = parser.parse_args()

print(args)
print(args.arg1)
print(args.arg2**2)
