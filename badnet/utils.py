import logging
import argparse
from decouple import config

#LOGGER
logging.basicConfig(filename='./log_badnet.log',level=logging.INFO)
logger = logging.getLogger(name='mylogger')

#ARGUMENT PARSER
parser = argparse.ArgumentParser()
parser.add_argument('--env', type=str, required=False, default=config("ENV"))
parser.add_argument('-r', '--reload', action='store_true', required=False, default=False, help='save new tournaments to DB without sending notifications')
args = parser.parse_args()