# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 Paul Cutler
#
# SPDX-License-Identifier: MIT
"""
`bambulabs`
================================================================================

A library to interface with a Bambu Labs 3D printer and query status and information


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

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/prcutler/CircuitPython_bambulabs.git"


class BambuPrinter:
    """Interface for a Bambu Labs 3D printer via MQTT.

    Communicates over two topics:

    * ``device/{serial}/report`` — subscribed to receive all printer state
    * ``device/{serial}/request`` — published to send commands

    On connect, automatically requests a full state bootstrap (``pushall``,
    ``get_version``, ``get_history``).

    :param mqtt_client: A configured ``adafruit_minimqtt.MQTT`` instance pointed
        at the printer's IP/hostname with the correct credentials.
    :param serial_number: The printer's serial number string, used to build
        MQTT topic paths.
    """

    def __init__(self, mqtt_client, serial_number):
        self._mqtt = mqtt_client
        self._serial = serial_number
        self._report_topic = "device/{}/report".format(serial_number)
        self._request_topic = "device/{}/request".format(serial_number)
        self._print_state = {}
        self._info_state = {}
        self._upgrade_state = {}
        self._system_state = {}

        self._mqtt.on_connect = self._on_connect
        self._mqtt.on_message = self._on_message

    # ---- Internal ----------------------------------------------------------

    def _on_connect(self, client, _userdata, _flags, _rc):
        client.subscribe(self._report_topic)
        self.pushall()
        self.info_get_version()
        self.request_firmware_history()

    def _on_message(self, _client, _topic, message):
        try:
            data = json.loads(message)
        except Exception:
            return
        if "print" in data:
            self._print_state.update(data["print"])
        if "info" in data:
            self._info_state.update(data["info"])
        if "upgrade" in data:
            self._upgrade_state.update(data["upgrade"])
        if "system" in data:
            self._system_state.update(data["system"])

    def _publish(self, payload):
        self._mqtt.publish(self._request_topic, json.dumps(payload))

    # ---- Connection --------------------------------------------------------

    def connect(self):
        """Establish the MQTT connection to the printer."""
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

    # ---- State bootstrap ---------------------------------------------------

    def pushall(self):
        """Request a full state update from the printer (use sparingly)."""
        self._publish({"pushing": {"command": "pushall"}})

    def info_get_version(self):
        """Request hardware and firmware version information."""
        self._publish({"info": {"sequence_id": "0", "command": "get_version"}})

    def request_firmware_history(self):
        """Request firmware version history."""
        self._publish({"upgrade": {"sequence_id": "0", "command": "get_history"}})

    def dump(self):
        """Return all cached printer state as a dict with keys ``print``, ``info``,
        ``upgrade``, and ``system``."""
        return {
            "print": self._print_state,
            "info": self._info_state,
            "upgrade": self._upgrade_state,
            "system": self._system_state,
        }

    # ---- Temperature -------------------------------------------------------

    @property
    def bed_temperature(self):
        """Current bed temperature in degrees Celsius."""
        return self._print_state.get("bed_temper")

    @property
    def bed_temperature_target(self):
        """Target bed temperature in degrees Celsius."""
        return self._print_state.get("bed_target_temper")

    @bed_temperature_target.setter
    def bed_temperature_target(self, temperature):
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "gcode_line",
                    "param": "M140 S{}\n".format(int(temperature)),
                }
            }
        )

    @property
    def nozzle_temperature(self):
        """Current nozzle temperature in degrees Celsius."""
        return self._print_state.get("nozzle_temper")

    @property
    def nozzle_temperature_target(self):
        """Target nozzle temperature in degrees Celsius."""
        return self._print_state.get("nozzle_target_temper")

    @nozzle_temperature_target.setter
    def nozzle_temperature_target(self, temperature):
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "gcode_line",
                    "param": "M104 S{}\n".format(int(temperature)),
                }
            }
        )

    @property
    def chamber_temperature(self):
        """Current chamber temperature in degrees Celsius."""
        return self._print_state.get("chamber_temper")

    # ---- Fan speeds --------------------------------------------------------

    @property
    def part_fan_speed(self):
        """Part cooling fan speed (0-255)."""
        return self._print_state.get("cooling_fan_speed")

    @part_fan_speed.setter
    def part_fan_speed(self, speed):
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "gcode_line",
                    "param": "M106 P1 S{}\n".format(int(speed)),
                }
            }
        )

    @property
    def aux_fan_speed(self):
        """Auxiliary fan speed (0-255)."""
        return self._print_state.get("big_fan1_speed")

    @aux_fan_speed.setter
    def aux_fan_speed(self, speed):
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "gcode_line",
                    "param": "M106 P2 S{}\n".format(int(speed)),
                }
            }
        )

    @property
    def chamber_fan_speed(self):
        """Chamber fan speed (0-255)."""
        return self._print_state.get("big_fan2_speed")

    @chamber_fan_speed.setter
    def chamber_fan_speed(self, speed):
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "gcode_line",
                    "param": "M106 P3 S{}\n".format(int(speed)),
                }
            }
        )

    # ---- Print progress ----------------------------------------------------

    @property
    def print_percentage(self):
        """Current print completion percentage (0-100)."""
        return self._print_state.get("mc_percent")

    @property
    def remaining_time(self):
        """Estimated remaining print time in minutes."""
        return self._print_state.get("mc_remaining_time")

    @property
    def current_layer(self):
        """Current layer number being printed."""
        return self._print_state.get("layer_num")

    @property
    def total_layers(self):
        """Total number of layers in the print job."""
        return self._print_state.get("total_layer_num")

    @property
    def gcode_file(self):
        """Filename of the currently active gcode file."""
        return self._print_state.get("gcode_file")

    @property
    def subtask_name(self):
        """Current print subtask/job name."""
        return self._print_state.get("subtask_name")

    @property
    def print_speed(self):
        """Current print speed level (0=silent, 1=standard, 2=sport, 3=ludicrous)."""
        return self._print_state.get("spd_lvl")

    @property
    def gcode_state(self):
        """Printer gcode state string (e.g. RUNNING, PAUSE, FAILED, FINISH)."""
        return self._print_state.get("gcode_state")

    @property
    def print_error_code(self):
        """Current print error code, or 0 if none."""
        return self._print_state.get("print_error")

    # ---- Print control -----------------------------------------------------

    def pause_print(self):
        """Pause the current print job."""
        self._publish({"print": {"sequence_id": "0", "command": "pause"}})

    def resume_print(self):
        """Resume a paused print job."""
        self._publish({"print": {"sequence_id": "0", "command": "resume"}})

    def stop_print(self):
        """Stop the current print job."""
        self._publish({"print": {"sequence_id": "0", "command": "stop"}})

    def set_print_speed(self, speed_lvl=1):
        """Set the print speed level.

        :param speed_lvl: 0=silent, 1=standard, 2=sport, 3=ludicrous.
        """
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "print_speed",
                    "param": str(int(speed_lvl)),
                }
            }
        )

    def send_gcode(self, gcode_command):
        """Send a raw G-code command string to the printer.

        :param gcode_command: G-code string, e.g. ``"G28\\n"``.
        """
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "gcode_line",
                    "param": gcode_command,
                }
            }
        )

    def skip_objects(self, obj_list):
        """Skip specified objects during the current print.

        :param obj_list: List of object index integers to skip.
        """
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "skip_objects",
                    "obj_list": obj_list,
                }
            }
        )

    def start_print_3mf(
        self,
        filename,
        plate_number=1,
        use_ams=True,
        ams_mapping=None,
        skip_objects=None,
        flow_calibration=False,
    ):
        """Start printing a 3MF file stored on the printer.

        :param filename: Path to the 3MF file on the printer's storage.
        :param plate_number: Plate index to print (default 1).
        :param use_ams: Whether to use the AMS (default ``True``).
        :param ams_mapping: AMS tray mapping list (optional).
        :param skip_objects: List of object indices to skip (optional).
        :param flow_calibration: Enable flow calibration (default ``False``).
        """
        payload = {
            "print": {
                "sequence_id": "0",
                "command": "project_file",
                "param": "Metadata/plate_{}.gcode".format(plate_number),
                "subtask_name": filename,
                "url": "file:///mnt/sdcard/{}".format(filename),
                "bed_type": "auto",
                "timelapse": False,
                "bed_leveling": True,
                "flow_cali": flow_calibration,
                "vibration_cali": False,
                "layer_inspect": False,
                "use_ams": use_ams,
            }
        }
        if ams_mapping is not None:
            payload["print"]["ams_mapping"] = ams_mapping
        if skip_objects is not None:
            payload["print"]["obj_list"] = skip_objects
        self._publish(payload)

    # ---- Lighting ----------------------------------------------------------

    def turn_light_on(self):
        """Turn the chamber LED on."""
        self._publish(
            {
                "system": {
                    "sequence_id": "0",
                    "command": "ledctrl",
                    "led_node": "chamber_light",
                    "led_mode": "on",
                }
            }
        )

    def turn_light_off(self):
        """Turn the chamber LED off."""
        self._publish(
            {
                "system": {
                    "sequence_id": "0",
                    "command": "ledctrl",
                    "led_node": "chamber_light",
                    "led_mode": "off",
                }
            }
        )

    @property
    def light_state(self):
        """Chamber light state from the system ``lights_report`` list."""
        return self._system_state.get("lights_report")

    # ---- Filament / AMS ----------------------------------------------------

    def load_filament(self):
        """Load filament into the printer."""
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "ams_change_filament",
                    "target": 255,
                    "curr_temp": 220,
                    "tar_temp": 220,
                }
            }
        )

    def unload_filament(self):
        """Unload filament from the printer."""
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "ams_change_filament",
                    "target": 254,
                    "curr_temp": 220,
                    "tar_temp": 220,
                }
            }
        )

    def resume_filament_action(self):
        """Resume a paused filament load/unload operation."""
        self._publish(
            {"print": {"sequence_id": "0", "command": "ams_control", "param": "resume"}}
        )

    def set_filament(self, filament_material, colour, ams_id=255, tray_id=254):
        """Set filament type and colour for a tray.

        :param filament_material: Filament material string (e.g. ``"PLA"``).
        :param colour: Colour hex string without ``#`` (e.g. ``"FFFFFF"``).
        :param ams_id: AMS unit index (default ``255`` for external spool).
        :param tray_id: Tray index within the AMS (default ``254``).
        """
        self._publish(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "ams_filament_setting",
                    "ams_id": ams_id,
                    "tray_id": tray_id,
                    "tray_color": "{}FF".format(colour),
                    "nozzle_temp_min": 190,
                    "nozzle_temp_max": 240,
                    "tray_type": filament_material,
                }
            }
        )

    @property
    def ams_status(self):
        """AMS filament/tray status data dict from the print state."""
        return self._print_state.get("ams")

    @property
    def vt_tray(self):
        """External spool (virtual tray) properties dict."""
        return self._print_state.get("vt_tray")

    # ---- Nozzle ------------------------------------------------------------

    @property
    def nozzle_type(self):
        """Installed nozzle type string."""
        return self._print_state.get("nozzle_type")

    @property
    def nozzle_diameter(self):
        """Installed nozzle diameter in mm."""
        return self._print_state.get("nozzle_diameter")

    def set_nozzle_info(self, nozzle_type, nozzle_diameter=0.4):
        """Configure the nozzle type and diameter.

        :param nozzle_type: Nozzle type string (e.g. ``"hardened_steel"``).
        :param nozzle_diameter: Nozzle diameter in mm (default ``0.4``).
        """
        self._publish(
            {
                "system": {
                    "sequence_id": "0",
                    "command": "set_accessories",
                    "accessory_type": "nozzle",
                    "nozzle_type": nozzle_type,
                    "nozzle_diameter": str(nozzle_diameter),
                }
            }
        )

    # ---- Calibration -------------------------------------------------------

    def auto_home(self):
        """Home all printer axes."""
        self.send_gcode("G28\n")

    def calibration(
        self,
        bed_levelling=True,
        motor_noise_cancellation=False,
        vibration_compensation=False,
    ):
        """Run printer calibration routines.

        :param bed_levelling: Enable bed levelling (default ``True``).
        :param motor_noise_cancellation: Enable motor noise cancellation (default ``False``).
        :param vibration_compensation: Enable vibration compensation (default ``False``).
        """
        option = (
            (1 if bed_levelling else 0)
            | (2 if vibration_compensation else 0)
            | (4 if motor_noise_cancellation else 0)
        )
        self._publish(
            {"print": {"sequence_id": "0", "command": "calibration", "option": option}}
        )

    def set_bed_height(self, height):
        """Set the Z-axis bed position.

        :param height: Height integer 0-256.
        """
        self.send_gcode("G0 Z{}\n".format(int(height)))

    # ---- Firmware ----------------------------------------------------------

    @property
    def firmware_version(self):
        """Current OTA firmware version string, or ``None`` if not yet received."""
        modules = self._info_state.get("module", [])
        for module in modules:
            if isinstance(module, dict) and module.get("name") == "ota":
                return module.get("sw_ver")
        return None

    def upgrade_firmware(self, override=False):
        """Upgrade the printer firmware.

        :param override: Force upgrade even if already up to date (default ``False``).
        """
        self._publish(
            {
                "upgrade": {
                    "sequence_id": "0",
                    "command": "upgrade_confirm",
                    "src_id": 1,
                    "force": override,
                }
            }
        )

    def get_firmware_history(self):
        """Request the firmware version history."""
        self._publish({"upgrade": {"sequence_id": "0", "command": "get_history"}})

    # ---- System ------------------------------------------------------------

    @property
    def wifi_signal(self):
        """WiFi signal strength in dBm."""
        return self._print_state.get("wifi_signal")

    def reboot(self):
        """Reboot the printer."""
        self._publish({"system": {"sequence_id": "0", "command": "reboot"}})

    def get_access_code(self):
        """Request the local access code from the printer."""
        self._publish({"system": {"sequence_id": "0", "command": "get_access_code"}})

    def set_timelapse(self, enable):
        """Enable or disable onboard timelapse recording.

        :param enable: ``True`` to enable, ``False`` to disable.
        """
        self._publish(
            {
                "camera": {
                    "sequence_id": "0",
                    "command": "ipcam_record_set",
                    "control": "enable" if enable else "disable",
                }
            }
        )
