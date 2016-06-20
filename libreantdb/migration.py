from elasticsearch.helpers import scan, bulk


# Migration from _timestamp special field to _insertion_date

missing_insertion_date_query = {
        "constant_score" : {
            "filter" : { "missing" : { "field" : "_insertion_date" } }
        }
    }


def elements_without_insertion_date(es, indexname):
    return es.count(index=indexname, body={'query': missing_insertion_date_query})['count']


def migrate_timestamp(es, indexname):
    query = {"fields": ["_timestamp", "_source"],
             "query": missing_insertion_date_query}

    def update_action_gen():
        scanner = scan(es,
                       index=indexname,
                       query=query)
        for v in scanner:
            if "_timestamp" in v:
                timestamp = v['_timestamp']
            elif 'fields' in v and '_timestamp' in v['fields']:
                timestamp = v['fields']['_timestamp']
            else:
                raise Exception("Cannot find '_timestamp' field on volume with id: '{}'".format(v['_id']))

            yield { '_op_type': 'update',
                    '_index': indexname,
                    '_type': v['_type'],
                    '_id': v['_id'],
                    'doc':{'_insertion_date': timestamp}
                  }
    return bulk(es, update_action_gen())
