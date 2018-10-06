#!/usr/bin/env python

import logging
logging.basicConfig(
    #level=logging.DEBUG,
    level=logging.INFO,
    # Match squid log output
    format='%(asctime)s| %(name)s/%(process)d: %(message)s '
            '@%(funcName)s:%(lineno)d #%(levelname)s',
    datefmt='%Y/%m/%d %H:%M:%S'
)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import sys
import os

aws_region = os.environ['AWS_REGION']
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

import boto.ec2
conn = boto.ec2.connect_to_region(
    aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

#import boto.route53
#conn = boto.route53.connect_to_region(
#    aws_region,
#    aws_access_key_id=aws_access_key_id,
#    aws_secret_access_key=aws_secret_access_key,
#)

def main():
    print True


if __name__ == '__main__':
    main()
