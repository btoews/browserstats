import requests
import json

with open('browserscope.json','r') as f:
  j = json.loads(f.read())

# caniuse data
caniuse = json.loads(requests.get("https://raw.github.com/Fyrd/caniuse/master/data.json").text)

with open('stats/index.json','r') as f:
  index = json.loads(f.read())

# There are naming descrepencies between caniuse and browserscope. 
# This is my best attempt at reconciling these.
ua_translations = {
  'Opera Mini 5'    : 'Opera Mini 5.0-7.0',
  'Opera Mini 6'    : 'Opera Mini 5.0-7.0',
  'Opera Mini 7'    : 'Opera Mini 5.0-7.0',
  'Blackberry 7'    : 'Blackberry Browser 7',
  'Android 2'       : 'Android Browser 2.3',
  'Android 4'       : 'Android Browser 4',
  'Opera Mobile 12' : 'Opera Mobile 12.1',
  'Mobile Safari 4' : 'iOS Safari 4.2-4.3',
  'Mobile Safari 5' : 'iOS Safari 5.0-5.1'
}

agent_translations = {
  'Firefox'          : 'firefox',
  'Blackberry'       : 'bb',
  'Chrome'           : 'chrome',
  'Opera Mini'       : 'op_mini',
  'iOS Safari'       : 'ios_saf',
  # 'and_ff'
  'Opera'            : 'opera',
  'Opera Mobile'     : 'op_mob',
  'Safari'           : 'safari',
  # 'and_chr'
  'Android Browser'  : 'android',
  'IE': 'ie',
}

val_translations = {
  'yes': True,
  'no':  False
}

# Got this list from the caniuse data
known_versions = {u'Opera': [u'12', u'12.1'], u'Opera Mini': [u'5.0-7.0'], u'Chrome for Android': [u'0'], u'Opera Mobile': [u'12.1'], u'Chrome': [u'24', u'25', u'26', u'27', u'21', u'22', u'23', u'11', u'13', u'12', u'15', u'14', u'17'], u'iOS Safari': [u'6', u'4.2-4.3', u'5.0-5.1'], u'Firefox for Android': [], u'Safari': [u'5.1', u'5', u'4', u'6'], u'Firefox': [u'3.6', u'20', u'3', u'5', u'4', u'9', u'8', u'11', u'10', u'13', u'12', u'15', u'14', u'17', u'16', u'19', u'18'], u'Android Browser': [u'4.1', u'4.2', u'4', u'2.3', u'2.2', u'2.1'], u'IE': [u'10', u'7', u'6', u'9', u'8'], u'Blackberry Browser': [u'7']}

features = {}

# suck out all the data into a sane format
for browser in j['results']:
  # translate the name if necessary
  trans_browser = ua_translations.get(browser,browser)

  # parse the ua name
  trans_browser = browser.split(' ')
  version = trans_browser[-1]
  family  = ' '.join(trans_browser[0:-1])

  # make sure we are dealing with a known version
  if family not in known_versions.keys(): continue
  if version not in known_versions[family]: continue

  for feature in j['results'][browser]['results']:
    features.setdefault(feature,{})
    features[feature].setdefault(family,{})
    features[feature][family].setdefault(version,False)
    features[feature][family][version] = val_translations[j['results'][browser]['results'][feature]['result']]

feature_output = []
for feature in features:
  print "feature: %s" % repr(feature)
  feature_data = {
    "feature_name": feature,
    "feature_description": feature,
    "feature_links": [],
    "children": []
  }

  index_entry = {
    "categories": ["Security"],
    "file"      : "stats/%s.json" % feature,
    "title"     : feature
    }

  if feature not in map(lambda f: f['title'], index["features"]):
    index["features"].append(index_entry)

  for family in features[feature]:
    agent_data = {
      "family_name": family,
      "children": []
    }

    for version in features[feature][family]:
      version_data = {
        "version_name": version,
        "size": caniuse["agents"][agent_translations[family]]["usage_global"][version],
        "support": features[feature][family][version]
      }

      if version_data["size"] > .08:
        agent_data['children'].append(version_data)
    feature_data['children'].append(agent_data)
  feature_output.append(feature_data)

  feature_output_text = json.dumps(feature_data)
  feature_file = "stats/%s.json" % feature

  # write the JSON to its own file
  with open(feature_file, "w") as f:
    f.write(feature_output_text)

if "Security" not in index['categories']:
  index["categories"].append("Security")

index["features"].sort(key=lambda x:x['title'])

with open("stats/index.json","w") as f:
  f.write(json.dumps(index))
