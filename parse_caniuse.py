import json
import requests

# Its not always y/n. This translates it into that.
SUPPORT_VALUES = {
    "n": False,
    "p": False,
    "u": False,
    "y": True,
    "y x": True,
    "a": True,
    "a x": True
  }

parsed = json.loads(requests.get("https://raw.github.com/Fyrd/caniuse/master/data.json").text)

features = []
categories = set()

for feature in parsed["data"]:
  feature_data = {
    "feature_name": parsed["data"][feature]["title"],
    "feature_description": parsed["data"][feature]["description"],
    "feature_links": parsed["data"][feature]["links"],
    "children": []
  }

  for agent in parsed["agents"]:
    agent_data = {
      "family_name": parsed["agents"][agent]["browser"],
      "children": []
    }

    for version in parsed['agents'][agent]['usage_global']:
      version_data = {
        "version_name": version,
        "size": parsed["agents"][agent]["usage_global"][version],
        "support": False
      }

      # Don't sweat the small stuff...
      # if version_data["size"] > .01:
      # raw support value
      support = parsed["data"][feature]["stats"].get(agent,{}).get(version,False)

      # parse the raw support value
      version_data["support"] = SUPPORT_VALUES.get(support,False)

      # add version as a child of the browser family
      agent_data["children"].append(version_data)

    # add browser family as a child of the feature
    feature_data["children"].append(agent_data)

  # convert the feature data to JSON
  feature_output = json.dumps(feature_data)
  feature_file = "stats/%s.json" % feature

  [categories.add(c) for c in parsed["data"][feature]["categories"] if c]

  features.append(
    {
      "title": parsed["data"][feature]["title"],
      "file": feature_file,
      "categories": parsed["data"][feature]["categories"]
    })

  # write the JSON to its own file
  with open(feature_file, "w") as f:
    f.write(feature_output)

features.sort(key=lambda x:x['title'])

categories = list(categories)
categories.sort()

index = {
  "features": features,
  "categories": categories
}

with open("./stats/index.json","w") as f:
  f.write(json.dumps(index))



