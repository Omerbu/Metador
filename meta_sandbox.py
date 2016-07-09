"""Sandbox Module for Dev team to fuck with"""

from __future__ import print_function
import sys
import mr_acoustid
import json
from meta_utils import FuncTimeitWrapper

API_KEY = 'JKMQc1GXqS'

@FuncTimeitWrapper
def aidmatch(filename, parsed=True):


    try:
        results, org_duration = mr_acoustid.match(API_KEY, filename,parse=parsed)
    except mr_acoustid.NoBackendError:
        print("chromaprint library/tool not found", file=sys.stderr)
        sys.exit(1)
    except mr_acoustid.FingerprintGenerationError:
        print("fingerprint could not be calculated", file=sys.stderr)
        sys.exit(1)
    except mr_acoustid.WebServiceError as exc:
        print("web service request failed:", exc.message, file=sys.stderr)
        sys.exit(1)

    if parsed:
        for score, match_duration, title, artist in results:
            print(artist, title)
            print(match_duration)
            score_string = "Score: {}%".format(int(score*100))
            print(score_string)
        print("original duration:{}".format(org_duration))
        print("-------------------------")
    else:
        with open('json_test.json', 'w') as outfile:
            json.dump(results, outfile, indent=4, sort_keys=True, separators=(',', ':'))


if __name__ == '__main__':
    aidmatch('test_files/opera.flac', True)
