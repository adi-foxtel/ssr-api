from setuptools import setup, find_packages

setup(name='ssr_api',
      version='0.0.dev0',
      description=('mySql and Oracle API layer for talking to databases'),
      url='https://github.com/adi-foxtel/ssr-api.git',
      author='Adi Saric',
      author_email='adi.saric@foxtel.com.au',
      license='Copyright (C) Foxtel, Inc - All Rights Reserved',
      packages=find_packages(),
      scripts=[
            'scripts/apifast.py'
      ],
      install_requires=[

            'xmltodict',
            'fastapi',
            'uvicorn',
            'starlette_exporter',
            'pyasn1',
            'pyasn1_modules',
            'requests',
            'fastapi_utils',
            'mysql-connector-python',
            'oracledb'

      ],
      zip_safe=True)
