from setuptools import setup, find_packages

setup(name='beliefs',
      version='0.1',
      install_requires=['distribute', 'colormath'],
      description=['Partial-information datastructures used to represent belief states'],
      url="https://github.com/EventTeam/beliefs",
      author='Dustin Smith',
      author_email='dustin@media.mit.edu',
      package_dir={'':'src'},
      modules=['beliefstate'],
      packages=['beliefs.cells'])
