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

from controllers.stp.message import Message, Payload, Frame, AbstractResponse

class CommandMessage(object):
    
    OPERATION_START = 1
    OPERATION_STOP  = 2
    OPERATION_RESET = 4
    
    def __init__(self):
        self.payload = Payload(None, True)
        self.payload.set_control()
        self.payload.set_command('E')
        self.frame = Frame(self.payload)
	self.frame.set_terminating(True)
        self.message = Message()
        self.message.add_frame(self.frame)
        
    def get_message(self):
        return self.message
    
    def set_operation(self, op):
        op = int(op)
        if not op in [self.OPERATION_START, self.OPERATION_STOP, self.OPERATION_RESET]:
            raise ValueError("operation not defined")

        str_op = str(op).zfill(2)
        self.payload.set_parameter(0, str_op)
    
class CommandResponse(AbstractResponse):
    
    def _is_valid(self):
        frame = self.msg.get_frame(0)
        payload = frame.get_payload()
        
        return payload.get_type() == Payload.TYPE_QUERY
