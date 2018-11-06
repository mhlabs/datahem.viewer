#!/usr/bin/env python

from google.cloud import bigquery
import os, json, re, logging

log = logging.getLogger(__name__)

def run_authorized_view(shared_view_id, group_email, sql):

    client = bigquery.Client()
    sql = sql.format(project=client.project)

# Crate the read-only dataset if not already exist
    m = re.search('(.*)@.*', group_email)
    shared_dataset_id = m.group(1).replace('.','_')
    shared_dataset = bigquery.Dataset(client.dataset(shared_dataset_id+'_ro'))
    shared_dataset.location = 'EU'
    try:
        shared_dataset = client.create_dataset(shared_dataset)  # API request
    except Exception, e:
        log.error(str(e))

# Authorize the group to access the shared read-only dataset
    try:
        access_entries = shared_dataset.access_entries
        access_entries.append(bigquery.AccessEntry('READER', 'groupByEmail', group_email))
        shared_dataset.access_entries = access_entries
        shared_dataset = client.update_dataset(shared_dataset, ['access_entries'])  # API request
    except Exception, e:
        log.error(str(e))

# Create the shared view in the new dataset. First delete view if it already exists
    try:
        table = client.get_table(shared_dataset.table(shared_view_id))
        if(table.view_query != None):
            client.delete_table(shared_dataset.table(shared_view_id))
    except Exception, e:
        log.error(str(e))

    view = bigquery.Table(shared_dataset.table(shared_view_id))
    view.view_query = sql
    try:
        view = client.create_table(view)  # API request
    except Exception, e:
        log.error(str(e))
        return False

# Authorize the view to access the source dataset
    m = re.findall('.*`.*\.(.*)\..*`.*', sql)
    for row in m:
        try:
            source_dataset = client.get_dataset(client.dataset(row)) # API request
            access_entries = list(source_dataset.access_entries)
            access_entries.append(bigquery.AccessEntry(None, 'view', view.reference.to_api_repr()))
            source_dataset.access_entries = access_entries
            source_dataset = client.update_dataset(source_dataset, ['access_entries'])  # API request
        except Exception, e:
            log.error(str(e))

# Crate the read-write dataset if not already exist
    m = re.search('(.*)@.*', group_email)
    shared_dataset_id = m.group(1).replace('.','_')
    shared_dataset = bigquery.Dataset(client.dataset(shared_dataset_id+'_rw'))
    shared_dataset.location = 'EU'
    try:
        shared_dataset = client.create_dataset(shared_dataset)  # API request
    except Exception, e:
        log.error(str(e))

# Authorize the group to access the shared read-write dataset
    try:
        access_entries = shared_dataset.access_entries
        access_entries.append(bigquery.AccessEntry('WRITER', 'groupByEmail', group_email))
        shared_dataset.access_entries = access_entries
        shared_dataset = client.update_dataset(shared_dataset, ['access_entries'])  # API request
    except Exception, e:
        log.error(str(e))

    return True

# Read view definitions from json-files in the views directory and generate datasets and views accordingly
def read_view_definition_files():
    views = []
    path_to_json = 'views/'
    json_files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path_to_json)) for f in fn if f.endswith('.json')]
    for row in json_files:
        shared_view_id = re.search('.*/(.*)\.json', row).group(1)
        with open(row) as json_file:
            json_text = json.load(json_file)
            sql = json_text['sql']
            groups = json_text['groups']
            for group in groups:
                views.append((shared_view_id, group, sql))
    return views


def iterate_views(views):
    length = len(views)
    i = 0
    while i < length:
        view = views.pop()
        if not run_authorized_view(view[0], view[1], view[2]):
            views.insert(0,view)
        i+=1
    #Not elegant dependency algorithm/graph, but if number of views doesn't diminish in an iteration -> broken dependencies. Else, continue until no more views to generate
    if (len(views) < length and len(views) > 0):
        iterate_views(views)

if __name__ == '__main__':
    views = read_view_definition_files()
    iterate_views(views)