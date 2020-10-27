# Edwards-STP-iX455
Python implementation for Edwards STP iX455 Turbo Pump

# How-to Use
The Edwards-STP-ix455 library depends on the serial and e21_util packages, however e21_util can be neglected if you import the serial package exlicitly.
```python

from e21_util.transport import Serial
# Alternatively, this should work as well
# from serial import Serial

from stp_ix455.protocol import STPProtocol
from stp_ix455.driver import STPDriver

# Setup your logging as you want.
# Setting logger = None will disable the logging
import logging
logger = logging.getLogger(__name__)

# device path is platform dependent
device_path = '/dev/ttyUSBxxx'

serial_connection = Serial(device_path, 9600, 8, 'N', 1, 2)
stp_protocol = STPProtocol(logger=logger)
stp_driver = STPDriver(serial_connection, stp_protocol)

# Starts/Stops the turbo pump
stp_driver.start()
stp_driver.stop()
```
