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

from stp_ix455.message import Message, Payload, Frame, AbstractResponse
from stp_ix455.messages.ReadOptionFunc import ReadOptionFuncResponse

class SetOptionFuncMessage(object):
    
    REMOTE_OPERATION_MODE_X2 = 0x01
    REMOTE_OPERATION_MODE_X3 = 0x02
    REMOTE_OPERATION_MODE_X5 = 0x05
    REMOTE_OPERATION_MODE_POWER_SUPPLY = 0x06
    REMOTE_OPERATION_MODE_COMMUNICATION_UNIT = 0x07
    
    def __init__(self, readresponse):
        
        if not isinstance(readresponse, ReadOptionFuncResponse):
            raise TypeError("resonse must be an instance of ReadOptionFuncResponse")
        
        read_payload = readresponse.get_response().get_frame(0).get_payload().get_raw()
        
        self.payload = Payload(read_payload, True)
        self.payload.set_control()
        self.payload.set_command('=')
        self.frame = Frame(self.payload)
        self.message = Message()
        self.message.add_frame(self.frame)
    
    def set_remote_operation_mode(self, mode):
        mode = int(mode)
        if not mode in [self.REMOTE_OPERATION_MODE_X2, self.REMOTE_OPERATION_MODE_X3, self.REMOTE_OPERATION_MODE_X5, self.REMOTE_OPERATION_MODE_POWER_SUPPLY, self.REMOTE_OPERATION_MODE_COMMUNICATION_UNIT]:
            raise ValueError("mode not defined")

        str_mode = str(mode).zfill(2)
        self.payload.set_parameter(0, str_mode)
        
    def get_message(self):
        return self.message
        
class SetOptionFuncResponse(AbstractResponse):
    pass