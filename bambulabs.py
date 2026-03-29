# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Paul Cutler
#
# SPDX-License-Identifier: MIT
"""
`bambulabs`
================================================================================

A library to interface with a Bambu Labs 3D printer and query status.


* Author(s): Paul Cutler

Implementation Notes
--------------------

**Hardware:**

Requires a Bambu Labs 3D printer and Bambu Labs Makerworld account.

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

import json
import os
import time
import wifi
import adafruit_connection_manager
import adafruit_minimqtt.adafruit_minimqtt as MQTT


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/prcutler/CircuitPython_bambulabs.git"


pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)

# BAMBU MQTT settings - Bambu Cloud
bambu_broker = os.getenv("BAMBU_BROKER")
access_token = os.getenv("BAMBU_ACCESS_TOKEN")
user_id = os.getenv("USER_ID")
bambu_ip = os.getenv("BAMBU_IP")

# Set up MQTT client
mqtt_client = MQTT.MQTT(
    broker=bambu_broker,
    port=8883,
    username=user_id,
    password=access_token,
    socket_pool=pool,
    ssl_context=ssl_context,
    is_ssl=True,
)


class PrinterStatus:
    """Wraps the raw JSON dict returned by a ``pushall`` response and exposes
    each printer field as a named, readable property.

    All values come from the snapshot captured at the time ``pushall`` was
    called.  Use :attr:`raw` to access the complete original dict.

    :param data: The raw JSON dict received from the printer's report topic.
    """

    def __init__(self, data):
        self._data = data
        self._print = data.get("print", {})
        self._info = data.get("info", {})
        self._system = data.get("system", {})
        self._upgrade = data.get("upgrade", {})

    @property
    def raw(self):
        """The complete raw JSON dict from the printer."""
        return self._data

    # ---- Print state -------------------------------------------------------

    @property
    def gcode_state(self):
        """Printer gcode state string (e.g. ``RUNNING``, ``PAUSE``, ``FINISH``)."""
        return self._print.get("gcode_state")

    @property
    def print_percentage(self):
        """Current print completion percentage (0–100)."""
        return self._print.get("mc_percent")

    @property
    def remaining_time(self):
        """Estimated remaining print time in minutes."""
        return self._print.get("mc_remaining_time")

    @property
    def current_layer(self):
        """Current layer number being printed."""
        return self._print.get("layer_num")

    @property
    def total_layers(self):
        """Total number of layers in the print job."""
        return self._print.get("total_layer_num")

    @property
    def gcode_file(self):
        """Filename of the currently active gcode file."""
        return self._print.get("gcode_file")

    @property
    def subtask_name(self):
        """Current print subtask / job name."""
        return self._print.get("subtask_name")

    @property
    def print_speed(self):
        """Print speed level (0=silent, 1=standard, 2=sport, 3=ludicrous)."""
        return self._print.get("spd_lvl")

    @property
    def print_error_code(self):
        """Current print error code, or ``0`` if none."""
        return self._print.get("print_error")

    # ---- Temperatures ------------------------------------------------------

    @property
    def nozzle_temperature(self):
        """Current nozzle temperature in degrees Celsius."""
        return self._print.get("nozzle_temper")

    @property
    def nozzle_temperature_target(self):
        """Target nozzle temperature in degrees Celsius."""
        return self._print.get("nozzle_target_temper")

    @property
    def bed_temperature(self):
        """Current bed temperature in degrees Celsius."""
        return self._print.get("bed_temper")

    @property
    def bed_temperature_target(self):
        """Target bed temperature in degrees Celsius."""
        return self._print.get("bed_target_temper")

    @property
    def chamber_temperature(self):
        """Current chamber temperature in degrees Celsius."""
        return self._print.get("chamber_temper")

    # ---- Fan speeds --------------------------------------------------------

    @property
    def part_fan_speed(self):
        """Part cooling fan speed (0–255)."""
        return self._print.get("cooling_fan_speed")

    @property
    def aux_fan_speed(self):
        """Auxiliary fan speed (0–255)."""
        return self._print.get("big_fan1_speed")

    @property
    def chamber_fan_speed(self):
        """Chamber fan speed (0–255)."""
        return self._print.get("big_fan2_speed")

    # ---- Nozzle ------------------------------------------------------------

    @property
    def nozzle_type(self):
        """Installed nozzle type string (e.g. ``"brass"``)."""
        return self._print.get("nozzle_type")

    @property
    def nozzle_diameter(self):
        """Installed nozzle diameter in mm."""
        return self._print.get("nozzle_diameter")

    # ---- Filament / AMS ----------------------------------------------------

    @property
    def ams_status(self):
        """AMS filament / tray status dict, or ``None`` if no AMS present."""
        return self._print.get("ams")

    @property
    def vt_tray(self):
        """External spool (virtual tray) properties dict."""
        return self._print.get("vt_tray")

    # ---- System ------------------------------------------------------------

    @property
    def wifi_signal(self):
        """WiFi signal strength string (e.g. ``"-45dBm"``)."""
        return self._print.get("wifi_signal")

    @property
    def light_state(self):
        """Chamber light state list from the system ``lights_report`` field."""
        return self._system.get("lights_report")

    # ---- Firmware ----------------------------------------------------------

    @property
    def firmware_version(self):
        """Current OTA firmware version string, or ``None`` if not present."""
        modules = self._info.get("module", [])
        for module in modules:
            if isinstance(module, dict) and module.get("name") == "ota":
                return module.get("sw_ver")
        return None


class BambuPrinter:
    """Connect to a Bambu Labs printer over MQTT and query its status.

    :param mqtt_client: A configured ``adafruit_minimqtt.MQTT`` instance.
    :param serial_number: The printer's serial number, used to build MQTT topics.
    :param response_timeout: Seconds to wait for a printer response (default 10).
    """

    def __init__(self, mqtt_client, serial_number, response_timeout=10):
        self._mqtt = mqtt_client
        self._serial = serial_number
        self._response_timeout = response_timeout
        self._report_topic = "device/{}/report".format(serial_number)
        self._request_topic = "device/{}/request".format(serial_number)
        self._last_response = None

        self._mqtt.on_connect = self._on_connect
        self._mqtt.on_message = self._on_message

    # ---- Internal ----------------------------------------------------------

    def _on_connect(self, client, _userdata, _flags, _rc):
        client.subscribe(self._report_topic)

    def _on_message(self, _client, _topic, message):
        try:
            data = json.loads(message)
        except Exception:
            return
        self._last_response = data

    def _send_and_wait(self, payload):
        """Publish *payload* and block until the printer responds or timeout.

        :returns: The raw JSON response dict, or ``None`` on timeout.
        """
        self._last_response = None
        self._mqtt.publish(self._request_topic, json.dumps(payload))
        deadline = time.monotonic() + self._response_timeout
        while self._last_response is None and time.monotonic() < deadline:
            self._mqtt.loop()
            time.sleep(0.05)
        return self._last_response

    # ---- Connection --------------------------------------------------------

    def connect(self):
        """Establish the MQTT connection to the printer."""
        print(f"Connecting to Bambu printer at {bambu_ip}...")
        self._mqtt.connect()

    def loop(self):
        """Process pending MQTT messages. Call regularly in your main loop."""
        self._mqtt.loop()

    def loop_forever(self):
        """Block and loop indefinitely, processing MQTT messages."""
        self._mqtt.loop_forever()

    def is_connected(self):
        """Return ``True`` if the MQTT client is currently connected."""
        return self._mqtt.is_connected()

    # ---- Queries -----------------------------------------------------------

    def pushall(self):
        """Request a full state snapshot from the printer.

        :returns: A :class:`PrinterStatus` instance, or ``None`` on timeout.
        """
        response = self._send_and_wait({"pushing": {"command": "pushall"}})
        if response is not None:
            return PrinterStatus(response)
        return None

    def get_version(self):
        """Request hardware and firmware version information.

        :returns: The raw JSON response dict, or ``None`` on timeout.
        """
        return self._send_and_wait({"info": {"sequence_id": "0", "command": "get_version"}})

    def get_firmware_history(self):
        """Request the firmware version history.

        :returns: The raw JSON response dict, or ``None`` on timeout.
        """
        return self._send_and_wait({"upgrade": {"sequence_id": "0", "command": "get_history"}})
