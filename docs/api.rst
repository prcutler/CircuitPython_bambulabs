
API Reference
#############

.. automodule:: bambulabs

BambuPrinter
============

.. autoclass:: bambulabs.BambuPrinter
    :members:
    :member-order: bysource

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
