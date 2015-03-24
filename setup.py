import os
import sys
import msgfmt

from setuptools import setup
from setuptools.command.install_lib import install_lib as _install_lib
from setuptools.command.develop import develop as _develop
from distutils.command.build import build as _build
from setuptools.command.test import test as TestCommand
from distutils.cmd import Command


class compile_translations(Command):
    description = 'compile message catalogs to .mo files'
    user_options = [('force', 'f', "compile also not updated message catalogs")]
    boolean_options = ['force']

    def initialize_options(self):
        self.force = False

    def finalize_options(self):
        pass

    def run(self):
        """
           Compile all message catalogs .mo files into .po files.
           Skips not changed file based on source mtime.
        """
        # thanks to deluge guys ;)
        po_dir = os.path.join(os.path.dirname(__file__), 'webant','translations')
        print('Compiling po files from "{}"...'.format(po_dir))
        for lang in os.listdir(po_dir):
            sys.stdout.write("\tCompiling {}... ".format(lang))
            sys.stdout.flush()
            curr_lang_path = os.path.join(po_dir,lang)
            for path, dirs, filenames in os.walk(curr_lang_path):
                for f in filenames:
                    if f.endswith('.po'):
                        src = os.path.join(path, f)
                        dst = os.path.join(path, f[:-3]+".mo")
                        if not os.path.exists(dst) or self.force:
                            msgfmt.make(src, dst)
                            print("ok.")
                        else:
                            src_mtime = os.stat(src)[8]
                            dst_mtime = os.stat(dst)[8]
                            if src_mtime > dst_mtime:
                                msgfmt.make(src, dst)
                                print("ok.")
                            else:
                                print("already up to date.")
        print('Finished compiling translation files.')


class build(_build):
    sub_commands =  [('compile_translations', None)] + _build.sub_commands


class install_lib(_install_lib):
    def run(self):
        self.run_command('compile_translations' )
        _install_lib.run(self)


class develop(_develop):
     def run(self):
        self.run_command('compile_translations' )
        _develop.run(self)


class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests'])


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as buf:
        return buf.read()

setup(name='libreant',
      version='0.1.3',
      description='{e,}book archive focused on small grass root archives, distributed search, low assumptions',
      long_description=read('README.rst'),
      author='insomnialab',
      author_email='insomnialab@hacari.org',
      url='https://github.com/insomnia-lab/libreant',
      license='AGPL',
      packages=['libreantdb', 'webant', 'presets'],
      install_requires=[
          'gevent',
          'elasticsearch',
          'flask-bootstrap',
          'Flask-Babel',
          'flask-script',
          'Flask',
          'opensearch',
          'Fsdb==0.2.5'
      ],
      package_data = {
            # If any package contains *.mo include them:
            # important! leave all the stars!
            'webant': ['translations/*/*/*.mo']
        },
      include_package_data=True,
      tests_require=['nose', 'coverage'],
      zip_safe=False,
      cmdclass={'build': build,
                'test': NoseTestCommand,
                'install_lib': install_lib,
                'develop':develop,
                'compile_translations': compile_translations },
      entry_points={'console_scripts': [
          'webant=webant.webant:main',
          'libreant-manage=webant.manage:main',
          'agherant=webant.agherant_standalone:main'
      ] },
      classifiers=[
                  "Framework :: Flask",
                  "License :: OSI Approved :: GNU Affero General Public License v3",
                  "Operating System :: POSIX :: Linux",
                  "Programming Language :: Python :: 2",
                  "Development Status :: 4 - Beta"
                  ]
      )
