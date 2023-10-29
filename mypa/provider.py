from operator import attrgetter

import requests
from packaging.specifiers import SpecifierSet
from packaging.tags import sys_tags
from packaging.utils import canonicalize_name, parse_wheel_filename
from resolvelib import AbstractProvider

from .candidate import Candidate


class Provider(AbstractProvider):

    def __init__(self, python_version):
        self.python_version = python_version

    def identify(self, requirement_or_candidate):
        # 一意の名前の取得
        # https://packaging.pypa.io/en/stable/utils.html
        return canonicalize_name(requirement_or_candidate.name)

    def is_satisfied_by(self, requirement, candidate):
        # Package BとPackage Aが同じか
        # 同じであればAが持つ条件の中にBのバージョンが入っているか
        if canonicalize_name(requirement.name) != candidate.name:
            return False
        return candidate.version in requirement.specifier

    def get_preference(self, identifier, resolutions, candidates, information, backtrack_causes):
        # あるPackageを探索する優先度
        # 一旦依存が多いものを優先的に探索するようにしてみる
        # candidatesの中はIteratorMappingなのでsum
        return sum(1 for _ in candidates[identifier])

    def get_dependencies(self, candidate):
        # 依存の取得 packaging.requirements.Requirementのリストを返す
        return candidate.get_dependencies()

    def find_matches(self, identifier, requirements, incompatibilities):
        # identifierに対するファイルの候補リストを取得する

        # pypiのsimple apiからの情報取得
        data = requests.get(f"https://pypi.org/simple/{identifier}", headers={"Accept": "application/vnd.pypi.simple.v1+json"}).json()

        # 候補の選定
        candidates = []
        requirement_specifiers = [r.specifier for r in requirements[identifier]]  # そのpackageが依存している元の条件
        bad_versions = {c.version for c in incompatibilities[identifier]}  # そのpackageが依存解決に失敗したバージョン
        fp = ''.join(self.python_version.split('.')[:2])
        target_system_tags = {x for x in sys_tags() if x.interpreter in {f"cp{fp}", f"py{fp}", f"py{fp[0]}"}}  # 全system tag候補 ex: cp311-none-any

        for d in data["files"]:
            # wheelのみ対象とする
            if not d['url'].endswith('.whl'):
                continue

            # pythonバージョンが対応しているかを確認する
            if d["requires-python"] and self.python_version not in SpecifierSet(d['requires-python']):
                continue

            name, version, _, tags = parse_wheel_filename(d['filename'])

            # system tagが対応しているかを確認する
            if not tags & target_system_tags:
                continue

            # バージョンが噛み合っているものだけ追加
            if version not in bad_versions and all(version in x for x in requirement_specifiers):
                candidates.append(Candidate(name, version, d['url'], d['hashes'], d['core-metadata']))

        return sorted(candidates, key=attrgetter("version"), reverse=True)
