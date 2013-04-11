#!/bin/python
# -*- coding: utf-8 -*-


import redis

global_db = redis.Redis(port=6379, db=5)

r = redis.Redis(unix_socket_path='./redis_export.sock')

while True:
    key = r.spop('asns_details')
    if key is None:
        break
    date, source, a = key.split('|')
    asn_details = global_db.smembers(key)
    global_db.delete(key)
    blocks = global_db.mget(*[asn_detail + '|ips_block' for asn_detail in asn_details])

    p = global_db.pipeline(False)
    i = 0
    for asn_detail in asn_details:
        block = blocks[i]
        if block is None:
            print asn_detail + 'has no block.'
            exit()
        asn, ts = asn_detail.split('|')
        new_asn_detail = '{asn}|{block}'.format(asn=asn, block=block)
        p.sadd(key, new_asn_detail)
        p.rename('|'.join([asn_detail, date, source]), new_asn_detail)
        i += 1
    p.execute()