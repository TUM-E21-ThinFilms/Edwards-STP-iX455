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

class ReadOptionFuncMessage(object):
    
    def __init__(self):
        self.payload = Payload(None, True)
        self.payload.set_query()
        self.payload.set_command('=')
        self.frame = Frame(self.payload)
        self.message = Message()
        self.message.add_frame(self.frame)

    def get_message(self):
        return self.message

    def __str__(self):
        return "ReadOptions"
    
class ReadOptionFuncResponse(AbstractResponse):
    
    def get_remote_operation_mode(self):
        return self._raw_to_integer(self.msg.get_frame(0).get_payload().get_parameter(0, 2))    