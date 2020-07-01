import logging
import greeclimate.network_helper as nethelper

from enum import IntEnum, unique
from greeclimate.exceptions import DeviceNotBoundError
from greeclimate.network_helper import Props


@unique
class TemperatureUnits(IntEnum):
    C = 0
    F = 1


@unique
class Mode(IntEnum):
    Auto = 0
    Cool = 1
    Dry = 2
    Fan = 3
    Heat = 4


@unique
class FanSpeed(IntEnum):
    Auto = 0
    Low = 1
    MediumLow = 2
    Medium = 3
    MediumHigh = 4
    High = 5


@unique
class HorizontalSwing(IntEnum):
    Default = 0
    FullSwing = 1
    Left = 2
    LeftCenter = 3
    Center = 4
    RightCenter = 5
    Right = 6


@unique
class VerticalSwing(IntEnum):
    Default = 0
    FullSwing = 1
    FixedUpper = 2
    FixedUpperMiddle = 3
    FixedMiddle = 4
    FixedLowerMiddle = 5
    FixedLower = 6
    SwingUpper = 7
    SwingUpperMiddle = 8
    SwingMiddle = 9
    SwingLowerMiddle = 10
    SwingLower = 11


class Device:
    """Class representing a physical device, it's state and properties.

    Devices must be bound, either by discovering their presence, or supplying a persistent
    device key which is then used for communication (and encryption) with the unit. See the
    `bind` function for more details on how to do this.

    Once a device is bound occasionally call `update_state` to request and update state from
    the HVAC, as it is possible that it changes state from other sources.

    Attributes:
        power: A boolean indicating if the unit is on or off
        mode: An int indicating operating mode, see `Mode` enum for possible values
        target_temperature: The target temperature, ignore if in Auto, Fan or Steady Heat mode
        temperature_units: An int indicating unit of measurement, see `TemperatureUnits` enum for possible values
        fan_speed: An int indicating fan speed, see `FanSpeed` enum for possible values
        fresh_air: A boolean indicating if fresh air valve is open, if present
        xfan: A boolean to enable the fan to dry the coil, only used for cool and dry modes
        anion: A boolean to enable the ozone generator, if present
        sleep: A boolean to enable sleep mode, which adjusts temperature over time
        light: A boolean to enable the light on the unit, if present
        horizontal_swing: An int to control the horizontal blade position, see `HorizontalSwing` enum for possible values
        vertical_swing: An int to control the vertical blade position, see `VerticalSwing` enum for possible values
        quiet: A boolean to enable quiet operation
        turbo: A boolean to enable turbo operation (heat or cool faster initially)
        steady_heat: When enabled unit will maintain a target temperature of 8 degrees C
        power_save: A boolen to enable power save operation
    """

    def __init__(self, device_info):
        self._logger = logging.getLogger(__name__)

        self.device_info = device_info
        self.device_key = None

        """ Device properties """
        self._properties = None

    async def bind(self, key=None):
        """ Run the binding procedure.
        
        Binding is a finnicky procedure, and happens in 1 of 2 ways:
            1 - Without the key, binding must pass the device info structure immediately following
                the search devices procedure. There is only a small window to complete registration.
            2 - With a key, binding is implicit and no further action is required

            Both approaches result in a device_key which is used as like a persitent session id.

        Raises:
            socket.timeout: If binding was unsuccessful (the device didn't respond.)
        """

        self._logger.info("Starting device binding to %s", str(self.device_info))

        if key:
            self.device_key = key
        else:
            self.device_key = await nethelper.bind_device(self.device_info)

        if self.device_key:
            self._logger.info("Bound to device using key %s", self.device_key)

    async def update_state(self):
        """ Update the internal state of the device structure of the physical device """
        if not self.device_key:
            raise DeviceNotBoundError

        self._logger.debug("Updating device properties for (%s)", str(self.device_info))

        props = [x.value for x in Props]
        self._properties = nethelper.request_state(
            props, self.device_info, self.device_key
        )

    def get_property(self, name):
        """ Generic lookup of properties tracked from the physical device """
        if self._properties:
            return self._properties.get(name.value)
        return None

    def set_property(self, name, value):
        """ Generic setting of properties for the physical device """
        if not self._properties:
            self._properties = {}

        if self._properties.get(name.value) == value:
            return
        else:
            self._properties[name.value] = value

        self._logger.debug("Sending remote state update %s -> %s", name, value)
        nethelper.send_state({name.value: value}, self.device_info, key=self.device_key)

    @property
    def power(self) -> bool:
        return bool(self.get_property(Props.POWER))

    @power.setter
    def power(self, value):
        self.set_property(Props.POWER, int(value))

    @property
    def mode(self) -> int:
        return int(self.get_property(Props.MODE))

    @mode.setter
    def mode(self, value):
        self.set_property(Props.MODE, int(value))

    @property
    def target_temperature(self) -> int:
        return int(self.get_property(Props.TEMP_SET))

    @target_temperature.setter
    def target_temperature(self, value):
        self.set_property(Props.TEMP_SET, int(value))

    @property
    def temperature_units(self) -> int:
        return int(self.get_property(Props.TEMP_UNIT))

    @temperature_units.setter
    def temperature_units(self, value):
        self.set_property(Props.TEMP_UNIT, int(value))

    @property
    def fan_speed(self) -> int:
        return int(self.get_property(Props.FAN_SPEED))

    @fan_speed.setter
    def fan_speed(self, value):
        self.set_property(Props.FAN_SPEED, int(value))

    @property
    def fresh_air(self) -> bool:
        return bool(self.get_property(Props.FRESH_AIR))

    @fresh_air.setter
    def fresh_air(self, value):
        self.set_property(Props.FRESH_AIR, int(value))

    @property
    def xfan(self) -> bool:
        return bool(self.get_property(Props.XFAN))

    @xfan.setter
    def xfan(self, value):
        self.set_property(Props.XFAN, int(value))

    @property
    def anion(self) -> bool:
        return bool(self.get_property(Props.ANION))

    @anion.setter
    def anion(self, value):
        self.set_property(Props.ANION, int(value))

    @property
    def sleep(self) -> bool:
        return bool(self.get_property(Props.SLEEP))

    @sleep.setter
    def sleep(self, value):
        self.set_property(Props.SLEEP, int(value))

    @property
    def light(self) -> bool:
        return bool(self.get_property(Props.LIGHT))

    @light.setter
    def light(self, value):
        self.set_property(Props.LIGHT, int(value))

    @property
    def horizontal_swing(self) -> int:
        return int(self.get_property(Props.SWING_HORIZ))

    @horizontal_swing.setter
    def horizontal_swing(self, value):
        self.set_property(Props.SWING_HORIZ, int(value))

    @property
    def vertical_swing(self) -> int:
        return int(self.get_property(Props.SWING_VERT))

    @vertical_swing.setter
    def vertical_swing(self, value):
        self.set_property(Props.SWING_VERT, int(value))

    @property
    def quiet(self) -> bool:
        return bool(self.get_property(Props.QUIET))

    @quiet.setter
    def quiet(self, value):
        self.set_property(Props.QUIET, int(value))

    @property
    def turbo(self) -> bool:
        return bool(self.get_property(Props.TURBO))

    @turbo.setter
    def turbo(self, value):
        self.set_property(Props.TURBO, int(value))

    @property
    def steady_heat(self) -> bool:
        return bool(self.get_property(Props.STEADY_HEAT))

    @steady_heat.setter
    def steady_heat(self, value):
        self.set_property(Props.STEADY_HEAT, int(value))

    @property
    def power_save(self) -> bool:
        return bool(self.get_property(Props.POWER_SAVE))

    @power_save.setter
    def power_save(self, value):
        self.set_property(Props.POWER_SAVE, int(value))

