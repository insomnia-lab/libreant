import os

from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as buf:
        return buf.read()

setup(name='libreant',
      version='0.1',
      description='{e,}book archive, focused on small grass root archives, distributed search, low assumptions',
      long_description=read('README.mdwn'),
      author='boyska',
      author_email='piuttosto@logorroici.org',
      license='AGPL',
      packages=['libreantdb', 'webant'],
      install_requires=[
          'elasticsearch',
          'Flask',
          'flask-bootstrap',
          'flask-appconfig',
          'wtforms'
      ],
      tests_require=['nose'],
      test_suite='nose.collector',
      zip_safe=False,
      entry_points={
          'console_scripts': ['webant=webant.webant:main',
                              ]
      }
      )
