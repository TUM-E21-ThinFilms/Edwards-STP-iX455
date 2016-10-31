# Copyright (C) 2016, see AUTHORS.md
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from protocol import STPProtocol
from driver import STPDriver
from slave.transport import Serial
import logging

logger = logging.getLogger('Edwards STP-iX455')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('stppump.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

class STPPumpFactory:
    def create_pump(self):
        protocol = STPProtocol(logger=logger)
        protocol.set_name("Edwards STP Pump")
        return STPDriver(Serial('/dev/ttyUSB12', 9600, 8, 'N', 1, 2), protocol)
