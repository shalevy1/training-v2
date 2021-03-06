from base64 import b64encode
import json
import requests
import sys
import os
import flask
import sys, getopt
import boto3
from flask import render_template

WP_PAGE_IDS = { "index.part.html": {"dev": 93145, "prod": 92928},
                "00_AboutThisCourse.html": {"dev": 93147, "prod": 92932},
                "01_IntroductionToNeo4j.html": {"dev": 93148, "prod": 92935},
                "02_OverviewOfNeo4jAdministration.html": {"dev": 93149, "prod": 92937},
                "03_ManagingANeo4jDatabase.html": {"dev": 93150, "prod": 92939},
                "04_CausalClusteringInNeo4j.html": {"dev": 93151, "prod": 92941},
                "05_SecurityInNeo4j.html": {"dev": 93152, "prod": 92943},
                "06_MonitoringNeo4j.html": {"dev": 93153, "prod": 92945},
                "07_Summary.html": {"dev": 93154, "prod": 92947}
              }

fapp = flask.Flask('pub', template_folder='.')

'''
Get page content
'''
def get_page_content(filename):
  file = open('html/%s' % filename)
  return file.read()

'''
Publish file to S3 and get version
'''
def publish_app_js(stage, filename):
  global API_BASE_URL

  # Create an S3 client
  s3 = boto3.client('s3')

  with fapp.app_context():
    tmpl_vars = {'API_BASE_URL': API_BASE_URL[stage], 'STAGE': stage}
    rendered_content = render_template('js/' + filename, **tmpl_vars)

  f = s3.put_object(Body=bytes(rendered_content), Bucket='cdn.neo4jlabs.com', Key='graphacademy/neo4j-administration/' + stage + '/' + filename, ACL='public-read')
  print "\t\thttps://cdn.neo4jlabs.com/graphacademy/neo4j-administration/%s/%s?versionId=%s" % (stage, filename, f['VersionId'])
  return f['VersionId']


'''
Update wordpress page
'''
def update_wordpress_page(pageId, content):
    url = 'https://neo4j.com/wp-json/wp/v2/pages/%d' % (pageId)
    auth = b64encode('{}:{}'.format(os.getenv('PUBLISH_DOCS_USERNAME'), os.getenv('PUBLISH_DOCS_PASSWORD')))
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic {}'.format(auth),
    }

    r = requests.get(url, headers=headers)
    response = json.loads(r.content)

    # build response for update
    response['content'] = content
    headers['Content-Type'] = 'application/json'
    print "\t%s" % (url)
    pr = requests.post(url, headers=headers, data=json.dumps(response))
     
    return pr.content


def main(argv):
  stage = 'dev'
  try:
     opts, args = getopt.getopt(argv,"h",['stage='])
  except getopt.GetoptError:
     print 'publish.py --stage <stage>'
     sys.exit(2)
  for opt, arg in opts:
     if opt == '-h':
        print 'publish.py --stage <stage>'
        sys.exit()
     elif opt in ("--stage"):
        stage = arg
  print 'Stage is "%s"' % (stage)

  if stage <> 'dev' and stage <> 'prod':
    print "Stages 'prod' + 'dev' are only supported stages currently"
    sys.exit()

  if 'PUBLISH_DOCS_USERNAME' in os.environ and 'PUBLISH_DOCS_PASSWORD' in os.environ:
    # skip publishing JS as we'll publish separately before building web so asciidoc has URLs
    for key, value in WP_PAGE_IDS.iteritems():
      print "Publishing %s:" % (key)
      pageContent = update_wordpress_page(value[stage], get_page_content(key))
  else:
    print "Environment varisbles for PUBLISH_DOCS_USERNAME and PUBLISH_DOCS_PASSWORD must be set"
    sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])
