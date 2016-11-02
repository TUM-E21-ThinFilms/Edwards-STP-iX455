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

class ReadMeasMessage(object):
    def __init__(self):
        self.payload = Payload(None, True)
        self.payload.set_query()
        self.payload.set_command('D')
        self.frame = Frame(self.payload)
        self.message = Message()
        self.message.add_frame(self.frame)
        self.message.finish()
        
    def get_message(self):
        return self.message
    
class ReadMeasResponse(AbstractResponse):
    
    def _is_valid(self):
        frame = self.msg.get_frame(0)
        payload = frame.get_payload()
        
        return payload.get_type() == Payload.TYPE_CONTROL and payload.get_command() == 'D'
    
    # returns the rotation speed of the pump in rpm
    def get_rotation_speed(self):
        frame = self.msg.get_frame(0)
        payload = frame.get_payload()
        
        raw_data = payload.get_parameter(14, 4)
	    # convert Hz in rpm: * 60
        return self._raw_to_integer(raw_data) * 60
    
