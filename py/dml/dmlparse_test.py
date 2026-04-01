# © 2026 Intel Corporation
# SPDX-License-Identifier: MPL-2.0

from dml import dmlparse, toplevel, logging
import unittest
import re
import sys

def parse(contents):
    file_info = logging.FileInfo(
        '<unit test>', (1, 4), content_lines=contents.splitlines(
            keepends=True))
    ast = toplevel.parse(contents, file_info, file_info.name, (1, 4))
    assert ast.kind == 'dml', ast.kind
    return ast

class test_emptyprod_based_sites(unittest.TestCase):
    def test_calls_from_empty_rules(self):
        empty_prod_re = re.compile(r'[:|]\s*(?:$|\|)')
        assert empty_prod_re.search('foo : \n')
        assert not empty_prod_re.search('foo : something\n')

        for rules in (dmlparse.production_rules_dml12,
                      dmlparse.production_rules_dml14):
            for (name, rule) in rules.items():
                if name != 'p_error':
                    self.assertEqual(
                        bool(empty_prod_re.search(rule.__doc__)),
                        'fixup_emptyprod_lexpos' in rule.__code__.co_names,
                        f"bad production rule {name}: need fix_emptyprod_lexpos"
                        " call if and only if a production rule is empty")

    def test(self):
        # Test that sites are actually fixed up by fixup_emptyprod_lexpos.
        # Without it, sites would be ruined by empty production rules.
        ast = parse('''
method m() {}
    group g;
'''.strip())
        self.assertEqual((ast.site.lineno, ast.site.colno), (1, 1))
        [_, stmts] = ast.args
        self.assertEqual([stmt.kind for stmt in stmts], ['method', 'object'])
        self.assertEqual((stmts[0].site.lineno, stmts[0].site.colno), (1, 1))
        self.assertEqual((stmts[1].site.lineno, stmts[1].site.colno), (2, 5))
