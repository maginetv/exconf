# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from setuptools import find_packages
from setuptools import setup

setup(name='exconf',
      version='0.1.0',
      author=u'Hannu Varjoranta',
      author_email='hannu.varjoranta@magine.com',
      url='https://github.com/maginetv/exconf',
      description='Tool for managing service and different environment specific configurations.',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'exconf=exconf.cli:main',
          ]}
      )
