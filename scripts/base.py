import os
import sys
import json

import urllib2
import urllib

import pprint
import logging


default_vocab_file = './data/edc-vocabs.json'


import_properties = {}

with open('./config/import.ini', 'r') as config_file :
    for line in config_file :
        line = line.rstrip()
        
        if "=" not in line: continue
        if line.startswith("#") : continue
        
        key, value = line.split("=", 1)
        if value :
            value = value.strip()
        key = key.strip() 
        import_properties[key] = value

pprint.pprint(import_properties)
#Get the site_url and api_key used by most scripts.
site_url = import_properties['site_url']
api_key = import_properties['api_key']

def create_tag(vocab, tag):
    tag_dict = {'name': tag,
                'vocabulary_id': vocab['id']}
    data_string = urllib.quote(json.dumps(tag_dict))

    try:
        request = urllib2.Request(site_url + '/api/3/action/tag_create')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
        new_tag = response_dict['result']
        print '\tTag {0} added to the vocabulary.'.format(new_tag['display_name'])
    except Exception:
        pass


def create_vocab(vocab_name, tags):
    data_string = urllib.quote(json.dumps({'name': vocab_name}))
    try:
        request = urllib2.Request(site_url + '/api/3/action/vocabulary_create')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        vocab = response_dict['result']
        print '{0} is added to the vocabularies'.format(vocab['name'])
    except Exception, e:
        print "Exception in creating vocabulary ", str(e)
        return None

    if not vocab:
        return None

    for tag in tags:
        create_tag(vocab, tag)

    return vocab


def create_org(org_dict):

    org = None
    data_string =  urllib.quote(json.dumps({'id' : org_dict['name'], 'include_datasets': False}))
    try :
        request = urllib2.Request(site_url + '/api/3/action/organization_show')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        org = response_dict['result']
    except Exception:
        pass

    if not org:
        data_string =  urllib.quote(json.dumps(org_dict))
        try :
            request = urllib2.Request(site_url + '/api/3/action/organization_create')
            request.add_header('Authorization', api_key)
            response = urllib2.urlopen(request, data_string)
            assert response.code == 200

            response_dict = json.loads(response.read())
            assert response_dict['success'] is True

            org = response_dict['result']
        except Exception, e:
            print "Exception in creating organiztion ", str(e)
            pass
    return org


def edc_package_create(edc_record):


    data_string = urllib.quote(json.dumps(edc_record))

    pkg_dict = None
    errors = None
    try:
        request = urllib2.Request(site_url + '/api/3/action/package_create')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
#        pprint.pprint(response_dict)
        if response_dict['success'] == True :
            pkg_dict = response_dict['result']
        else:
            errors = response_dict['error']
    except Exception, e:
        print str(e)
        pass
    return (pkg_dict, errors)


#Return the name of an organization with the given id
def get_organization_id(org_title):

    data_string = urllib.quote(json.dumps({'all_fields': True}))
    try:
        request = urllib2.Request(site_url + '/api/3/action/organization_list')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        # package_create returns the created package as its result.
        orgs = response_dict['result']
    except:
        orgs = []

    for org in orgs:
        if org_title and org_title.startswith(org['title']) :
            return org['id']
    return None

def get_user_id(user_name):
    user_info = None
    data_string = urllib.quote(json.dumps({'id':user_name}))

    request = urllib2.Request(site_url + '/api/3/action/user_show')
    request.add_header('Authorization', api_key)
    try:
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        # package_create returns the created package as its result.
        user_info = response_dict['result']

        return user_info['id']

    except Exception:
        return None

