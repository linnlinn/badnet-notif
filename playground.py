import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--env', type=str, required=False, default='dev')
parser.add_argument('-r', '--reload', action='store_true', required=False, default=False, help='save new tournaments to DB without sending notifications')

args = parser.parse_args()

print(args.env, args.reload)

if any([1==0, 2==3]) and not args.reload:
    print('False')

if args.reload:
    print('True')
