import json


class Locker:

    @staticmethod
    def lock(candidates):
        info = {}
        for k, v in candidates.items():
            info[k] = {"name": k,
                       "version": v.version,
                       "url": v.url,
                       "hashes": v.hashes,
                       "core_metadata": v.core_metadata}
        with open('mypa.lock', 'w') as f:
            json.dump(info, f, indent=4)

    @staticmethod
    def read():
        with open('mypa.lock', 'r') as f:
            candidates = json.load(f)
        return candidates
