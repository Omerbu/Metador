"""
Module That receives a music file, run acoustid DB search and return match.

the results returned are a tuple-containing generator
and original track duration ("org_duration")

result-tuple format:
    (score, match_duration, title, artist)

    score = match percentage, represented by float.
    match_duration = matched track duration (not org_duration!)
    title, artist = self explanatory.

org_duration = original track duration (seconds).

"""
import sys
import mr_acoustid

API_KEY = 'JKMQc1GXqS'      # our API code for the project


def fingerprint_search(filename):
    """
    :param filename:
    :return: results (generator), org_duration

    Filename is either a local dir or a global dir.
    """
    try:
        results, org_duration = mr_acoustid.match(API_KEY, filename)
    except mr_acoustid.NoBackendError:
        print "chromaprint library/tool not found"
        sys.exit(1)
    except mr_acoustid.FingerprintGenerationError:
        print "fingerprint could not be calculated"
        sys.exit(1)
    except mr_acoustid.WebServiceError:
        print "web service request failed:"
        sys.exit(1)
    return results, org_duration
