# -*- coding: utf-8 -*-

#
# Copyright (C) 2011  Alex Yatskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import codecs
import json
import re


#
# Deinflection
#

class Deinflection:
    def __init__(self, term, tags=list(), rule=str()):
        self.children = list()
        self.term = term
        self.tags = tags
        self.rule = rule


    def deinflect(self, validator, rules, candidates):
        for rule, variants in rules.items():
            for variant in variants:
                tagsIn = variant['tagsIn']
                tagsOut = variant['tagsOut']
                kanaIn = variant['kanaIn']
                kanaOut = variant['kanaOut']

                allowed = len(self.tags) == 0
                for tag in self.tags:
                    if self.searchTags(tag, tagsIn):
                        allowed = True
                        break

                if not allowed or not self.term.endswith(kanaIn):
                    continue

                term = self.term[:-len(kanaIn)] + kanaOut
                candidates.update([term])

                child = Deinflection(term, tagsOut, rule)
                if child.deinflect(validator, rules, candidates):
                    self.children.append(child)

        if len(self.children) > 0:
            return True

        for tags in validator(self.term):
            if len(self.tags) == 0:
                return True

            for tag in self.tags:
                if self.searchTags(tag, tags):
                    return True


    def searchTags(self, tag, tags):
        for t in tags:
            if re.search(tag, t):
                return True


    def gather(self):
        if len(self.children) == 0:
            endpoint = {
                'root': self.term, 
                'term': self.term, 
                'rules': [self.rule] if self.rule else list()
            }

            return [endpoint]

        paths = list()
        for child in self.children:
            for path in child.gather():
                if self.rule:
                    path['rules'].append(self.rule)
                else:
                    path['term'] = self.term
                paths.append(path)

        return paths


#
# Deinflector
#

class Deinflector:
    def __init__(self, filename):
        with codecs.open(filename, 'rb', 'utf-8') as fp:
            self.rules = json.load(fp)


    def deinflect(self, term, validator):
        candidates = set()
        node = Deinflection(term)
        if node.deinflect(validator, self.rules, candidates):
            return node.gather(), candidates
