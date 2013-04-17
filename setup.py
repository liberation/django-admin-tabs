"""Setup script for django-admin-tabs"""
from setuptools import setup
from setuptools import find_packages


setup(
    name='django-admin-tabs',
    version='0.1',
    packages=find_packages(exclude=['example_project']),
    include_package_data=True,
    license='BSD License',
    description='Tabs for django.contrib.admin',
    long_description=open('README').read(),
    author='Djaz Team',
    author_email='devweb@liberation.fr',
    url='http://www.liberation.fr/',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ])
