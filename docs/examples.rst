Examples
########

Simple test
-----------

Connects to WiFi and to the printer via MQTT, requests a full state snapshot
with :meth:`~bambulabs.BambuPrinter.pushall`, and prints every available
status field — temperatures, fan speeds, print progress, nozzle info, and
the raw JSON response.

Requires the following keys in ``settings.toml``:

.. code-block:: toml

    CIRCUITPY_WIFI_SSID = "your-ssid"
    CIRCUITPY_WIFI_PASSWORD = "your-password"
    BAMBU_BROKER = "us.mqtt.bambulab.com"
    BAMBU_ACCESS_TOKEN = "your-access-token"
    USER_ID = "your-user-id"
    DEVICE_ID = "your-printer-serial-number"

.. literalinclude:: ../examples/bambulabs_simpletest.py
    :caption: examples/bambulabs_simpletest.py
    :linenos:
