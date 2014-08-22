from setuptools import setup

setup(name='facebook_api',
      version='0.1',
      description='Python lib to work with Facebook API',
      url='https://github.com/alandbarroso/facebook_python_api',
      author='Alan Dabien Barroso',
      author_email='alandbarroso@gmail.com',
      license='GLP 2.0',
      packages=['facebook_api', 'facebook_api.ads'],
      install_requires=[
          'httplib2',
      ],
      zip_safe=False)