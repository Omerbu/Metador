"""
Module That receives a music file, run acoustid DB search and return match.

the results returned are a tuple-containing generator.

result-tuple format:
    (score, rid, title, artist)
    score = match percentage, represented by float.
    rid = match-linked  musicBrainz page.
    title, artist = self explanatory.

Dev Comment:
    Until Paziko will find how to install the chromaprint library
    the fpcalc.exe have to be in the same dir as the filename.


"""
from __future__ import print_function
import sys
import acoustid

API_KEY = 'JKMQc1GXqS'      # our API code for the project

"""
encodes the messages to unicode in case of python 2.7
Not important for Metador project
"""
if sys.version_info[0] < 3:
    def print_(s):
        print(s.encode(sys.stdout.encoding, 'replace'))
else:
    def print_(s):
        print(s)


def fingerprint_search(filename):
    """
    :param filename:
    :return: results (generator)

    Filename is either a local dir or a global dir.
    """
    try:
        results = acoustid.match(API_KEY, filename)
    except acoustid.NoBackendError:
        print("chromaprint library/tool not found", file=sys.stderr)
        sys.exit(1)
    except acoustid.FingerprintGenerationError:
        print("fingerprint could not be calculated", file=sys.stderr)
        sys.exit(1)
    except acoustid.WebServiceError as exc:
        print("web service request failed:", exc.message, file=sys.stderr)
        sys.exit(1)
    return results

