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

from slave.driver import Driver, Command
from slave.types import Mapping, Float, String, Integer, Boolean, SingleType
from protocol import STPProtocol
from messages.Command import CommandMessage, CommandResponse
from messages.ReadFailMess import ReadFailMessMessage, ReadFailMessResponse
from messages.ReadMeas import ReadMeasMessage, ReadMeasResponse

class STPDriver(Driver):

    def __init__(self, transport, protocol=None):
        if protocol is None:
            protocol = STPProtocol()
        
        self.thread = None
        
        super(STPDriver, self).__init__(transport, protocol)

    def send_message(self, message):
        return self._protocol.query(self._transport, message.get_message())
	
    def clear(self):
	self._protocol.clear(self._transport)

    def start(self):
        msg = CommandMessage()
        msg.set_operation(CommandMessage.OPERATION_START)
        return CommandResponse(self.send_message(msg))
    
    def stop(self):
        msg = CommandMessage()
        msg.set_operation(CommandMessage.OPERATION_STOP)
        return CommandResponse(self.send_message(msg))
    
    def reset(self):
        msg = CommandMessage()
        msg.set_operation(CommandMessage.OPERATION_RESET)
        return CommandResponse(self.send_message(msg))
    
    def get_rotation(self):
        msg = ReadMeasMessage()
        return ReadMeasResponse(self.send_message(msg))
    
    def get_error(self):
        msg = ReadFailMessMessage()
        return ReadFailMessResponse(self.send_message(msg))
