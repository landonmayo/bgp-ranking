#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    :file:`bin/services/ranking_process.py` - Compute ranking
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Service which compute the ranking for each subnet/ASN we want to rank.
"""

import os
import sys
import ConfigParser
import time
import redis

from pubsublogger import publisher

sleep_timer = 10
key_to_rank = 'to_rank'


if __name__ == '__main__':

    publisher.channel = 'Ranking'

    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from ranking import compute

    history_db = redis.Redis(port = int(config.get('redis','port_cache')),
            db=config.get('redis','history'))
    i = 0

    publisher.info('{number} rank to compute'.\
            format(number = history_db.scard(key_to_rank)))
    compute.prepare()
    for i in range(10):
        if history_db.scard(key_to_rank) > 0 :
            break
        time.sleep(10)
    while history_db.scard(key_to_rank) > 0 :
        key = history_db.spop(key_to_rank)
        #try:
        if key is not None:
            compute.rank_using_key(key)
            i +=1
            if i%1000 == 0:
                publisher.info('{number} rank to compute'.\
                        format(number = history_db.scard(key_to_rank)))
        #except Exception as e:
            #history_db.sadd(key_to_rank, key)
        #    print e

    publisher.info('{number} ranks computed'.format(number = i))
