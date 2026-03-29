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
#. On your printer, go to Settings and obtain the IP address and copy it as
   ``BAMBU_IP``.

Misc. information
=================

This library queries your Bambu Labs 3D printer via the Bambu Cloud using MQTT 5.0.
Local mode is not supported due to it using MQTT 3.1.1. Issuing commands to your
Bambu printer is out of scope for this library.

API Reference
#############

.. automodule:: bambulabs

BambuPrinter
============

.. autoclass:: bambulabs.BambuPrinter
    :members:
    :member-order: bysource
    :no-index:

    **Connection**

    .. automethod:: connect
    .. automethod:: loop
    .. automethod:: loop_forever
    .. automethod:: is_connected

    **Queries**

    .. automethod:: pushall
    .. automethod:: get_version
    .. automethod:: get_firmware_history

PrinterStatus
=============

.. autoclass:: bambulabs.PrinterStatus
    :members:
    :member-order: bysource
    :no-index:

    **Raw data**

    .. autoattribute:: raw

    **Print state**

    .. autoattribute:: gcode_state
    .. autoattribute:: print_percentage
    .. autoattribute:: remaining_time
    .. autoattribute:: current_layer
    .. autoattribute:: total_layers
    .. autoattribute:: gcode_file
    .. autoattribute:: subtask_name
    .. autoattribute:: print_speed
    .. autoattribute:: print_error_code

    **Temperatures**

    .. autoattribute:: nozzle_temperature
    .. autoattribute:: nozzle_temperature_target
    .. autoattribute:: bed_temperature
    .. autoattribute:: bed_temperature_target
    .. autoattribute:: chamber_temperature

    **Fan speeds**

    .. autoattribute:: part_fan_speed
    .. autoattribute:: aux_fan_speed
    .. autoattribute:: chamber_fan_speed

    **Nozzle**

    .. autoattribute:: nozzle_type
    .. autoattribute:: nozzle_diameter

    **Filament / AMS**

    .. autoattribute:: ams_status
    .. autoattribute:: vt_tray

    **System**

    .. autoattribute:: wifi_signal
    .. autoattribute:: light_state

    **Firmware**

    .. autoattribute:: firmware_version
