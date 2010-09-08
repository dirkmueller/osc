import osc.core
import osc.oscerr
import os
import sys
from common import GET, PUT, POST, DELETE, OscTestCase
from xml.etree import cElementTree as ET
FIXTURES_DIR = os.path.join(os.getcwd(), 'repairwc_fixtures')

def suite():
    import unittest
    return unittest.makeSuite(TestRepairWC)

rev_dummy = '<revision rev="repository">\n  <srcmd5>empty</srcmd5>\n</revision>'

class TestRepairWC(OscTestCase):
    def _get_fixtures_dir(self):
        return FIXTURES_DIR

    def __assertNotRaises(self, exception, meth, *args, **kwargs):
        try:
            meth(*args, **kwargs)
        except exception:
            self.fail('%s raised' % exception.__name__)

    def test_working_empty(self):
        """consistent, empty working copy"""
        self._change_to_pkg('working_empty')
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    def test_working_nonempty(self):
        """
        consistent, non-empty working copy. One file is in conflict,
        one file is marked for deletion and one file has state 'A'
        """
        self._change_to_pkg('working_nonempty')
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    def test_buildfiles(self):
        """
        wc has a _buildconfig_prj_arch and a _buildinfo_prj_arch.xml in the storedir
        """
        self._change_to_pkg('buildfiles')
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    @GET('http://localhost/source/osctest/simple1/foo?rev=1', text='This is a simple test.\n')
    def test_simple1(self):
        """a file is marked for deletion but storefile doesn't exist"""
        self._change_to_pkg('simple1')
        self.assertRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')
        p = osc.core.Package('.', wc_check=False)
        p.wc_repair()
        self.assertTrue(os.path.exists(os.path.join('.osc', 'foo')))
        self._check_deletelist('foo\n')
        self._check_status(p, 'foo', 'D')
        self._check_status(p, 'nochange', 'M')
        self._check_status(p, 'merge', ' ')
        self._check_status(p, 'toadd1', '?')
        # additional cleanup check
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    def test_simple2(self):
        """a file "somefile" exists in the storedir which isn't tracked"""
        self._change_to_pkg('simple2')
        self.assertRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')
        p = osc.core.Package('.', wc_check=False)
        p.wc_repair()
        self.assertFalse(os.path.exists(os.path.join('.osc', 'somefile')))
        self._check_deletelist('foo\n')
        self._check_status(p, 'foo', 'D')
        self._check_status(p, 'nochange', 'M')
        self._check_status(p, 'merge', ' ')
        self._check_status(p, 'toadd1', '?')
        # additional cleanup check
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    def test_simple3(self):
        """toadd1 has state 'A' and a file .osc/toadd1 exists"""
        self._change_to_pkg('simple3')
        self.assertRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')
        p = osc.core.Package('.', wc_check=False)
        p.wc_repair()
        self.assertFalse(os.path.exists(os.path.join('.osc', 'toadd1')))
        self._check_deletelist('foo\n')
        self._check_status(p, 'foo', 'D')
        self._check_status(p, 'nochange', 'M')
        self._check_status(p, 'merge', ' ')
        self._check_addlist('toadd1\n')
        self._check_status(p, 'toadd1', 'A')
        # additional cleanup check
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    def test_simple4(self):
        """a file is listed in _to_be_deleted but isn't present in _files"""
        self._change_to_pkg('simple4')
        self.assertRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')
        p = osc.core.Package('.', wc_check=False)
        p.wc_repair()
        self._check_deletelist('foo\n')
        self._check_status(p, 'foo', 'D')
        self._check_status(p, 'nochange', 'M')
        self._check_status(p, 'merge', ' ')
        self._check_status(p, 'toadd1', '?')
        # additional cleanup check
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    def test_simple5(self):
        """a file is listed in _in_conflict but isn't present in _files"""
        self._change_to_pkg('simple5')
        self.assertRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')
        p = osc.core.Package('.', wc_check=False)
        p.wc_repair()
        self.assertFalse(os.path.exists(os.path.join('.osc', '_in_conflict')))
        self._check_deletelist('foo\n')
        self._check_status(p, 'foo', 'D')
        self._check_status(p, 'nochange', 'M')
        self._check_status(p, 'merge', ' ')
        self._check_status(p, 'toadd1', '?')
        # additional cleanup check
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    @GET('http://localhost/source/osctest/simple6/foo?rev=1', text='This is a simple test.\n')
    def test_simple6(self):
        """
        a file is listed in _to_be_deleted and is present
        in _files but the storefile is missing
        """
        self._change_to_pkg('simple6')
        self.assertRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')
        p = osc.core.Package('.', wc_check=False)
        p.wc_repair()
        self.assertTrue(os.path.exists(os.path.join('.osc', 'foo')))
        self._check_deletelist('foo\n')
        self._check_status(p, 'foo', 'D')
        self._check_status(p, 'nochange', 'M')
        self._check_status(p, 'merge', ' ')
        self._check_status(p, 'toadd1', '?')
        # additional cleanup check
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    def test_simple7(self):
        """files marked as skipped don't exist in the storedir"""
        self._change_to_pkg('simple7')
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    def test_simple8(self):
        """
        a file is marked as skipped but the skipped file exists in the storedir
        """
        self._change_to_pkg('simple8')
        self.assertRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')
        p = osc.core.Package('.', wc_check=False)
        p.wc_repair()
        self.assertFalse(os.path.exists(os.path.join('.osc', 'skipped')))
        self._check_deletelist('foo\n')
        self._check_status(p, 'foo', 'D')
        self._check_status(p, 'nochange', 'M')
        self._check_status(p, 'merge', ' ')
        self._check_status(p, 'toadd1', '?')
        self._check_status(p, 'skipped', 'S')
        # additional cleanup check
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

    @GET('http://localhost/source/osctest/multiple/merge?rev=1', text='Is it\npossible to\nmerge this file?I hope so...\n')
    @GET('http://localhost/source/osctest/multiple/nochange?rev=1', text='This file didn\'t change.\n')
    def test_multiple(self):
        """
        a storefile is missing, a file is listed in _to_be_deleted
        but is not present in _files, a file is listed in _in_conflict
        but the storefile is missing and a file exists in the storedir
        but is not present in _files
        """
        self._change_to_pkg('multiple')
        self.assertRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')
        p = osc.core.Package('.', wc_check=False)
        p.wc_repair()
        self.assertTrue(os.path.exists(os.path.join('.osc', 'foo')))
        self.assertFalse(os.path.exists(os.path.join('.osc', 'unknown_file')))
        self._check_deletelist('foo\n')
        self._check_status(p, 'foo', 'D')
        self._check_status(p, 'nochange', 'C')
        self._check_status(p, 'merge', ' ')
        self._check_status(p, 'foobar', 'A')
        self._check_status(p, 'toadd1', '?')
        # additional cleanup check
        self.__assertNotRaises(osc.oscerr.WorkingCopyInconsistent, osc.core.Package, '.')

if __name__ == '__main__':
    import unittest
    unittest.main()
