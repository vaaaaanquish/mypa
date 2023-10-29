from io import BytesIO
from zipfile import ZipFile

import requests
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.metadata import parse_email


class Candidate:

    def __init__(self, name, version, url, hashes, core_metadata):
        self.name = canonicalize_name(name)
        self.version = str(version)
        self.url = url
        self.hashes = hashes
        self.core_metadata = core_metadata
        self.metadata = None
        self.dependencies = None

    @staticmethod
    def _get_metadata(url):
        with ZipFile(BytesIO(requests.get(url).content)) as z:
            for n in z.namelist():
                if n.endswith(".dist-info/METADATA"):
                    return parse_email(z.open(n).read())
        return {}, {}

    def get_dependencies(self):
        if self.metadata is None:
            self.metadata, _ = self._get_metadata(self.url)
        if self.dependencies is None:
            deps = [Requirement(d) for d in self.metadata.get("requires_dist", [])]
            self.dependencies = [d for d in deps if d.marker is None]  # extrasのinstallはまた別
        return self.dependencies
