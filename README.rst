Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-bambulabs/badge/?version=latest
    :target: https://circuitpython-bambulabs.readthedocs.io/
    :alt: Documentation Status



.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/prcutler/CircuitPython_bambulabs/workflows/Build%20CI/badge.svg
    :target: https://github.com/prcutler/CircuitPython_bambulabs/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

A library to interface with a Bambu Labs 3D printer and query status and information


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================
.. note:: This library is not available on PyPI yet. Install documentation is included
   as a standard element. Stay tuned for PyPI availability!

.. todo:: Remove the above note if PyPI version is/will be available at time of release.

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-bambulabs/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-bambulabs

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-bambulabs

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install circuitpython-bambulabs

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install bambulabs

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Obtaining Your Printer Credentials and Save in settings.toml
============================================================

#. Login to `MakerWorld <https://makerworld.com/>`_.
#. Open the dev-tools (F12 in most browsers) and select
   ``Application > Cookies > https://makerworld.com``.
#. Copy the ``token`` string and save it as ``BAMBU_ACCESS_TOKEN`` in ``settings.toml``.
#. Access `https://makerworld.com/api/v1/design-user-service/my/preference
   <https://makerworld.com/api/v1/design-user-service/my/preference>`_ and copy
   ``uid`` as ``USER_ID``.
#. Access `https://makerworld.com/api/v1/iot-service/api/user/bind
   <https://makerworld.com/api/v1/iot-service/api/user/bind>`_ and copy
   ``dev_id`` as ``DEVICE_ID``.


You will need a ``settings.toml`` file with the following to connect via MQTT:

CIRCUITPY_WIFI_SSID = "your_wifi_ssid"
CIRCUITPY_WIFI_PASSWORD = "your_wifi_password"
BAMBU_BROKER = os.getenv("BAMBU_BROKER")
ACCESS_TOKEN = os.getenv("BAMBU_ACCESS_TOKEN")
USER_ID = os.getenv("USER_ID")
DEVICE_ID = "your_printer_serial_number"

Usage Example
=============

.. code-block:: python

    import json
    import os

    import wifi

    import bambulabs as bl

    # You will need a settings.toml file with the following to connect via MQTT:
    # bambu_broker = os.getenv("BAMBU_BROKER")
    # access_token = os.getenv("BAMBU_ACCESS_TOKEN")
    # user_id = os.getenv("USER_ID")
    # DEVICE_ID = "your_printer_serial_number"

    # Set up networking
    print("Connecting to AP...")
    wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
    print(f"Connected to {os.getenv('CIRCUITPY_WIFI_SSID')}")
    print(f"My IP address: {wifi.radio.ipv4_address}")

    device_id = os.getenv("DEVICE_ID")

    printer = bl.BambuPrinter(bl.mqtt_client, device_id)
    printer.connect()

    status = printer.pushall()

    if status is None:
        print("Timed out waiting for pushall response.")
    else:
        # Print out each individual status
        print("--- Printer Status ---")
        print(f"State:             {status.gcode_state}")
        print(f"File:              {status.gcode_file}")
        print(f"Job:               {status.subtask_name}")
        print(f"Progress:          {status.print_percentage}%")
        print(f"Remaining:         {status.remaining_time} min")
        print(f"Layer:             {status.current_layer} / {status.total_layers}")
        print(f"Print speed:       {status.print_speed}")
        print(f"Print error:       {status.print_error_code}")
        print(f"Nozzle temp:       {status.nozzle_temperature} / {status.nozzle_temperature_target} C")
        print(f"Bed temp:          {status.bed_temperature} / {status.bed_temperature_target} C")
        print(f"Chamber temp:      {status.chamber_temperature} C")
        print(f"Part fan:          {status.part_fan_speed}")
        print(f"Aux fan:           {status.aux_fan_speed}")
        print(f"Chamber fan:       {status.chamber_fan_speed}")
        print(f"Nozzle type:       {status.nozzle_type}")
        print(f"Nozzle diameter:   {status.nozzle_diameter} mm")
        print(f"WiFi signal:       {status.wifi_signal}")
        print(f"Light state:       {status.light_state}")
        print(f"Firmware version:  {status.firmware_version}")
        print()
        # Print the entire JSON response
        print("--- Raw JSON ---")
        print(json.dumps(status.raw))


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-bambulabs.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/prcutler/CircuitPython_bambulabs/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

This library was created with the assistance of Claude.  (I know, I know...)
