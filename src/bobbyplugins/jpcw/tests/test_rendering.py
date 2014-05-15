# -*- coding: utf-8 -*-

from shutil import rmtree
from tempfile import mkdtemp
import os
import stat
import unittest

import mock

from bobbyplugins.jpcw.rendering import (If_A_and_B_Statement,
                                         If_A_or_B_Statement,
                                         If_Not_Statement,
                                         If_Statement)

eps = [If_A_and_B_Statement, If_A_or_B_Statement, If_Not_Statement,
       If_Statement]


class render_structureTest(unittest.TestCase):

    def setUp(self):
        import bobbyplugins.jpcw
        import mrbobby.plugins
        mrbobby.plugins.PLUGINS['mr.bobby.render_filename'] = eps
        self.fs_tempdir = mkdtemp()
        self.fs_templates = os.path.abspath(
            os.path.join(os.path.dirname(bobbyplugins.jpcw.__file__),
                         'tests', 'templates'))

    def tearDown(self):
        rmtree(self.fs_tempdir)

    def call_FUT(self, template, variables, output_dir=None, verbose=True,
                 renderer=None, ignored_files=[]):
        from mrbobby.rendering import render_structure
        from mrbobby.rendering import jinja2_renderer

        if output_dir is None:
            output_dir = self.fs_tempdir

        if renderer is None:
            renderer = jinja2_renderer

        render_structure(
            template,
            output_dir,
            variables,
            verbose,
            renderer,
            ignored_files,
        )

    def test_subdirectories_created(self):
        from mrbobby.rendering import python_formatting_renderer

        self.call_FUT(os.path.join(self.fs_templates, 'unbound'),
                      {'ip_addr': '192.168.0.1',
                       'access_control': '10.0.1.0/16 allow',
                       'rdr.me': 'y'},
                      renderer=python_formatting_renderer,)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                  'usr/local/etc')))

    def test_subdirectories_not_created(self):
        from mrbobby.rendering import python_formatting_renderer
        self.call_FUT(os.path.join(self.fs_templates, 'unbound'),
                      {'ip_addr': '192.168.0.1',
                       'access_control': '10.0.1.0/16 allow',
                       'rdr.me': 'f'},
                      renderer=python_formatting_renderer,)
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                   'usr/local/etc')))
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir, 'etc')))
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                  'etc/rc.conf')))

    def test_skip_mrbobbyini_copying(self):
        self.call_FUT(os.path.join(self.fs_templates, 'skip_mrbobbyini'),
                      dict(foo='123'),)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir, 'test')))
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                   '.mrbobby.ini')))

    def test_ds_store(self):
        self.call_FUT(os.path.join(self.fs_templates, 'ds_store'),
                      dict(),)
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                   '.mrbobby.ini')))
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                   '.DS_Store')))

    def test_ignored(self):
        self.call_FUT(os.path.join(self.fs_templates, 'ignored'),
                      dict(),
                      ignored_files=['ignored', '*.txt', '.mrbobby.ini'],)
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                   '.mrbobby.ini')))
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                   'ignored')))
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                   'ignored.txt')))
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                  'not_ignored')))

    def test_string_replacement(self):
        from mrbobby.rendering import python_formatting_renderer
        self.call_FUT(os.path.join(self.fs_templates, 'unbound'),
                      {'ip_addr': '192.168.0.1',
                       'access_control': '10.0.1.0/16 allow',
                       'rdr.me': 'y'},
                      verbose=False,
                      renderer=python_formatting_renderer,)
        fs_unbound_conf = os.path.join(self.fs_tempdir,
                                       'usr/local/etc/unbound/unbound.conf')
        self.assertTrue('interface: 192.168.0.1' in
                        open(fs_unbound_conf).read())

    def test_directory_is_renamed(self):
        from mrbobby.rendering import python_formatting_renderer
        self.call_FUT(os.path.join(self.fs_templates, 'renamedir'),
                      {'name': 'blubber', 'rdr.me': 'y'},
                      verbose=False,
                      renderer=python_formatting_renderer,)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                  '/partsblubber/part')))

    def test_copied_file_is_renamed(self):
        from mrbobby.rendering import python_formatting_renderer
        self.call_FUT(os.path.join(self.fs_templates, 'renamedfile'),
                      {'name': 'blubber', 'rdr.me': 'y'},
                      verbose=False,
                      renderer=python_formatting_renderer,)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                  '/foo.blubber.rst')))

    def test_rendered_file_is_renamed(self):
        from mrbobby.rendering import python_formatting_renderer
        self.call_FUT(os.path.join(self.fs_templates, 'renamedtemplate'),
                      {'name': 'blubber', 'rdr.me': 'y', 'module': 'blather'},
                      verbose=False,
                      renderer=python_formatting_renderer,)
        fs_rendered = '%s/%s' % (self.fs_tempdir, '/blubber_endpoint.py')
        self.assertTrue(os.path.exists(fs_rendered))
        self.assertTrue('from blather import bar' in open(fs_rendered).read())

    def test_rendered_file_is_renamed_dotted_name(self):
        from mrbobby.rendering import python_formatting_renderer
        self.call_FUT(os.path.join(self.fs_templates, 'renamedtemplate2'),
                      {'author.name': 'foo', 'rdr.me': 'y'},
                      verbose=False,
                      renderer=python_formatting_renderer,)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                                  '/foo_endpoint.py')))

    def test_compount_renaming(self):
        """ all of the above edgecases in one fixture """
        from mrbobby.rendering import python_formatting_renderer
        self.call_FUT(os.path.join(self.fs_templates, 'renamed'),
                      {'name': 'blubber', 'rdr.me': 'y', 'module': 'blather'},
                      verbose=False,
                      renderer=python_formatting_renderer,)
        fs_rendered = '%s/%s' % (self.fs_tempdir,
                                 '/blatherparts/blubber_etc/blubber.conf')
        self.assertTrue(os.path.exists(fs_rendered))
        self.assertTrue('blather = blubber' in open(fs_rendered).read())


class render_templateTest(unittest.TestCase):
    def setUp(self):
        import bobbyplugins.jpcw
        import mrbobby.plugins
        mrbobby.plugins.PLUGINS['mr.bobby.render_filename'] = eps
        self.fs_tempdir = mkdtemp()
        dirname = os.path.dirname(bobbyplugins.jpcw.__file__)
        self.fs_templates = os.path.abspath(os.path.join(dirname, 'tests',
                                                         'templates'))

    def tearDown(self):
        rmtree(self.fs_tempdir)

    def call_FUT(self, template, variables, output_dir=None, verbose=False,
                 renderer=None):
        from mrbobby.rendering import render_template
        from mrbobby.rendering import python_formatting_renderer

        if output_dir is None:
            output_dir = self.fs_tempdir

        if renderer is None:
            renderer = python_formatting_renderer

        return render_template(
            template,
            output_dir,
            variables,
            verbose,
            renderer,
        )

    def test_render_copy(self):
        """if the source is not a template, it is copied."""
        fs_source = os.path.join(self.fs_templates, 'unbound/etc/rc.conf')

        fs_rendered = self.call_FUT(fs_source,
                                    {'ip_addr': '192.168.0.1',
                                     'access_control': '10.0.1.0/16 allow',
                                     'rdr.me': 'y'},)
        self.assertTrue(fs_rendered.endswith('rc.conf'))
        with open(fs_source) as f1:
            with open(fs_rendered) as f2:
                self.assertEqual(f1.read(), f2.read())

    def test_render_statement_template(self):
        """if the source is not a template, it is copied."""
        fnm = 'renamedtemplate2/+author.name++__if_rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.call_FUT(fs_source, {'rdr.me': 'y', 'author.name': 'bobby'},)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                       'bobby_endpoint.py')))

    def test_render_not_statement_template(self):
        """if the source is not a template, it is copied."""
        fnm = 'renamedtemplate3/+author.name+'\
              '+__if_not_rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.call_FUT(fs_source, {'rdr.me': 'n', 'author.name': 'bobby'},)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                       'bobby_endpoint.py')))

    def test_render_not_statement_template_with_true_value(self):
        """if the source is not a template, it is copied."""
        fnm = 'renamedtemplate3/+author.name+'\
              '+__if_not_rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.call_FUT(fs_source, {'rdr.me': 'y', 'author.name': 'bobby'},)
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                        'bobby_endpoint.py')))

    def test_render_not_statement_template_raise_unknown_var(self):
        """if the source is not a template, it is copied."""
        fnm = 'renamedtemplate3/+author.name+'\
              '+__if_not_rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.assertRaises(KeyError, self.call_FUT, fs_source,
                          {'a-rdr.me': 'y', 'c-rdr.me': 'y'})

    def test_render_if_A_or_B_statement_template_A_is_True(self):
        """if A or B statement."""
        fnm = 'if_a_or_b/+author.name+'\
              '+__if_a-rdr.me_or_b-rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.call_FUT(fs_source, {'a-rdr.me': 'y', 'b-rdr.me': 'n',
                                  'author.name': 'bobby'},)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                       'bobby_endpoint.py')))

    def test_render_if_A_or_B_statement_template_B_is_True(self):
        """if A or B statement."""
        fnm = 'if_a_or_b/+author.name+'\
              '+__if_a-rdr.me_or_b-rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.call_FUT(fs_source, {'a-rdr.me': 'n', 'b-rdr.me': 'y',
                                  'author.name': 'bobby'},)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                       'bobby_endpoint.py')))

    def test_render_if_A_or_B_statement_template_A_anb_B_are_False(self):
        """if A or B statement."""
        fnm = 'if_a_or_b/+author.name+'\
              '+__if_a-rdr.me_or_b-rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.call_FUT(fs_source, {'a-rdr.me': 'n', 'b-rdr.me': 'n',
                                  'author.name': 'bobby'},)
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                        'bobby_endpoint.py')))

    def test_render_if_A_or_B_statement_template_A_anb_C_are_True(self):
        """if A or B statement."""
        fnm = 'if_a_or_b/+author.name+'\
              '+__if_a-rdr.me_or_b-rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.assertRaises(KeyError, self.call_FUT, fs_source,
                          {'a-rdr.me': 'y', 'c-rdr.me': 'y'})

    def test_render_if_A_and_B_statement_template_A_is_True(self):
        """if A and B statement."""
        fnm = 'if_a_and_b/+author.name+'\
              '+__if_a-rdr.me_and_b-rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.call_FUT(fs_source, {'a-rdr.me': 'y', 'b-rdr.me': 'n',
                                  'author.name': 'bobby'},)
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                        'bobby_endpoint.py')))

    def test_render_if_A_and_B_statement_template_B_is_True(self):
        """if A and B statement."""
        fnm = 'if_a_and_b/+author.name+'\
              '+__if_a-rdr.me_and_b-rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.call_FUT(fs_source, {'a-rdr.me': 'n', 'b-rdr.me': 'y',
                                  'author.name': 'bobby'},)
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                        'bobby_endpoint.py')))

    def test_render_if_A_and_B_statement_template_A_anb_B_are_False(self):
        """if A and B statement."""
        fnm = 'if_a_and_b/+author.name+'\
              '+__if_a-rdr.me_and_b-rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.call_FUT(fs_source, {'a-rdr.me': 'n', 'b-rdr.me': 'n',
                                  'author.name': 'bobby'},)
        self.assertFalse(os.path.exists('%s/%s' % (self.fs_tempdir,
                                        'bobby_endpoint.py')))

    def test_render_if_A_and_B_statement_template_A_anb_B_are_True(self):
        """if A and B statement."""
        fnm = 'if_a_and_b/+author.name+'\
              '+__if_a-rdr.me_and_b-rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.call_FUT(fs_source, {'a-rdr.me': 'y', 'b-rdr.me': 'y',
                                  'author.name': 'bobby'},)
        self.assertTrue(os.path.exists('%s/%s' % (self.fs_tempdir,
                                       'bobby_endpoint.py')))

    def test_render_if_A_and_B_statement_template_A_anb_C_are_True(self):
        """if A and B statement."""
        fnm = 'if_a_and_b/+author.name+'\
              '+__if_a-rdr.me_and_b-rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        self.assertRaises(KeyError, self.call_FUT, fs_source,
                          {'a-rdr.me': 'y', 'c-rdr.me': 'y'})

    def test_render_false_statement_template_is_None(self):
        """if the source is not a template, it is copied."""
        fnm = 'renamedtemplate2/+author.name++__if_rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        fs_rendered = self.call_FUT(fs_source, {'rdr.me': 'n'},)
        self.assertEquals(fs_rendered, None)

    def test_render_any_non_true_value_statement_template_is_None(self):
        """if the source is not a template, it is copied."""
        fnm = 'renamedtemplate2/+author.name++__if_rdr.me__+_endpoint.py.bobby'
        fs_source = os.path.join(self.fs_templates, fnm)
        fs_rendered = self.call_FUT(fs_source, {'rdr.me': 'any value here'},)
        self.assertEquals(fs_rendered, None)

    def test_render_key_error_statement_template(self):
        """if the source is not a template, it is copied."""
        fnm = 'renamedtemplate2/+author.name++__if_rdr.me__+_endpoint.py.bobby'
        templ = os.path.join(self.fs_templates, fnm)
        self.assertRaises(KeyError, self.call_FUT, templ,
                          {'another_rdr.me': 'y'})

    def test_render_template(self):
        """if the source is a template, it is rendered and the target file
        drops the `.bobby` suffix."""
        fs_source = os.path.join(self.fs_templates,
                                 'unbound/+__if_rdr.me__+usr'
                                 '/local/etc/unbound/unbound.conf.bobby')
        fs_rendered = self.call_FUT(fs_source,
                                    {'ip_addr': '192.168.0.1',
                                     'access_control': '10.0.1.0/16 allow',
                                     'rdr.me': 'y'})
        self.assertTrue(fs_rendered.endswith('/unbound.conf'))
        self.assertTrue('interface: 192.168.0.1' in open(fs_rendered).read())

    def test_rendered_permissions_preserved(self):
        fs_source = os.path.join(self.fs_templates,
                                 'unbound/+__if_rdr.me__+usr'
                                 '/local/etc/unbound/unbound.conf.bobby')
        os.chmod(fs_source, 771)
        fs_rendered = self.call_FUT(fs_source,
                                    {'ip_addr': '192.168.0.1',
                                     'access_control': '10.0.1.0/16 allow',
                                     'rdr.me': 'y'})
        self.assertEqual(stat.S_IMODE(os.stat(fs_rendered).st_mode), 771)

    def test_render_missing_key(self):
        templ = os.path.join(self.fs_templates,
                             'unbound/+__if_rdr.me__+usr/local/etc/unbound/'
                             'unbound.conf.bobby')

        self.assertRaises(KeyError, self.call_FUT, templ, dict())

    def test_render_namespace(self):
        templ = os.path.join(self.fs_templates,
                             'missing_namespace_key/foo.bobby')

        filename = self.call_FUT(templ, {'foo.bar': '1'})
        with open(filename) as f:
            self.assertEqual(f.read(), '1\n')

    def test_render_namespace_jinja2(self):
        from mrbobby.rendering import jinja2_renderer
        templ = os.path.join(self.fs_templates,
                             'missing_namespace_key/foo_jinja2.bobby')

        filename = self.call_FUT(templ, {'foo.bar': '2'},
                                 renderer=jinja2_renderer)
        with open(filename) as f:
            self.assertEqual(f.read(), '2\n')

    def test_render_newline(self):
        from mrbobby.rendering import jinja2_renderer
        templ = os.path.join(self.fs_templates,
                             'missing_namespace_key/foo_jinja2.bobby')

        tfile = open(templ, 'r')
        self.assertEqual(tfile.read(), '{{{foo.bar}}}\n')

        filename = self.call_FUT(templ,
                                 {'foo.bar': '2'},
                                 renderer=jinja2_renderer)
        with open(filename) as f:
            self.assertEqual(f.read(), '2\n')

    def test_render_namespace_missing_key(self):
        templ = os.path.join(self.fs_templates,
                             'missing_namespace_key/foo.bobby')

        self.assertRaises(KeyError, self.call_FUT, templ, {})

    def test_render_missing_key_statement(self):
        templ = os.path.join(self.fs_templates,
                             'missing_namespace_key/foo.bobby')

        self.assertRaises(KeyError, self.call_FUT, templ, {'rdr.me': 'y'})

    def test_render_namespace_missing_key_jinja2(self):
        from jinja2 import UndefinedError
        from mrbobby.rendering import jinja2_renderer
        templ = os.path.join(self.fs_templates,
                             'missing_namespace_key/foo_jinja2.bobby')

        self.assertRaises(UndefinedError, self.call_FUT, templ, {},
                          renderer=jinja2_renderer)

    def test_jinja2_strict_undefined(self):
        from jinja2 import UndefinedError
        from mrbobby.rendering import jinja2_renderer

        templ = os.path.join(self.fs_templates,
                             'strict_undefined.bobby')

        self.assertRaises(UndefinedError, self.call_FUT, templ, {},
                          renderer=jinja2_renderer)


class render_filenameTest(unittest.TestCase):

    def call_FUT(self, filename, variables):
        from mrbobby.rendering import render_filename
        return render_filename(filename, variables)

    def test_filename_substitution(self):
        templ = self.call_FUT('em0_+ip_addr+.conf', dict(ip_addr='127.0.0.1'))
        self.assertEqual(templ, 'em0_127.0.0.1.conf')

    def test_filename_nested(self):
        templ = self.call_FUT('em0_+ip.addr+.conf', {'ip.addr': '127.0.0.1'})
        self.assertEqual(templ, 'em0_127.0.0.1.conf')

    def test_multiple_filename_substitution(self):
        templ = self.call_FUT('+device+_+ip_addr+.conf',
                              dict(ip_addr='127.0.0.1', device='em0'))
        self.assertEqual(templ, 'em0_127.0.0.1.conf')

    def test_single_plus_not_substituted(self):
        templ = self.call_FUT('foo+bar',
                              dict(foo='127.0.0.1', bar='em0'))
        self.assertEqual(templ, 'foo+bar')

    def test_no_substitution(self):
        templ = self.call_FUT('foobar',
                              dict(foo='127.0.0.1', bar='em0'))
        self.assertEqual(templ, 'foobar')

    def test_pluses_in_path(self):
        templ = self.call_FUT('+/bla/+/+bar+',
                              dict(bar='em0'))
        self.assertEqual(templ, '+/bla/+/em0')

    @mock.patch('mrbobby.rendering.os', sep='\\')
    def test_pluses_in_pathwindows(self, mock_sep):
        templ = self.call_FUT('+\\bla\\+\\+bar+',
                              dict(bar='em0'))
        self.assertEqual(templ, '+\\bla\\+\\em0')

    def test_missing_key(self):
        self.assertRaises(KeyError, self.call_FUT, 'foo+bar+blub', dict())

# vim:set et sts=4 ts=4 tw=80:
