# 16-标准UUID全表（Assigned Numbers 机器生成）

> 数据源：Bluetooth SIG 官方公开仓库 `bitbucket.org/bluetooth-SIG/public`（assigned_numbers/uuids/*.yaml），
> 2026-09-10 克隆生成；特征 511 项 · 服务 76 项 · 描述符 24 项 · 声明 4 项。
> UUID 表示：16 位短码（Base UUID `0000XXXX-0000-1000-8000-00805F9B34FB` 内嵌）。
> 再生方法：`git clone --depth 1 https://bitbucket.org/bluetooth-SIG/public.git` 后按同格式重生成；
> 字段结构语义见缓存规范 `80-参考资料/bluetooth/GATT_Specification_Supplement.pdf`（2026-02-05 版，
> 注意：现行 GSS 正文已不含 UUID 编号，编号以本表（Assigned Numbers）为单一事实源）。

## 声明（Declarations，0x2801 起）

| UUID | 名称 | SIG 标识 |
|---|---|---|
| 0x2800 | Primary Service | org.bluetooth.attribute.gatt.primary_service_declaration |
| 0x2801 | Secondary Service | org.bluetooth.attribute.gatt.secondary_service_declaration |
| 0x2802 | Include | org.bluetooth.attribute.gatt.include_declaration |
| 0x2803 | Characteristic | org.bluetooth.attribute.gatt.characteristic_declaration |

## 服务（Services，0x1800 起）

| UUID | 名称 | SIG 标识 |
|---|---|---|
| 0x1800 | GAP | org.bluetooth.service.gap |
| 0x1801 | GATT | org.bluetooth.service.gatt |
| 0x1802 | Immediate Alert | org.bluetooth.service.immediate_alert |
| 0x1803 | Link Loss | org.bluetooth.service.link_loss |
| 0x1804 | Tx Power | org.bluetooth.service.tx_power |
| 0x1805 | Current Time | org.bluetooth.service.current_time |
| 0x1806 | Reference Time Update | org.bluetooth.service.reference_time_update |
| 0x1807 | Next DST Change | org.bluetooth.service.next_dst_change |
| 0x1808 | Glucose | org.bluetooth.service.glucose |
| 0x1809 | Health Thermometer | org.bluetooth.service.health_thermometer |
| 0x180A | Device Information | org.bluetooth.service.device_information |
| 0x180D | Heart Rate | org.bluetooth.service.heart_rate |
| 0x180E | Phone Alert Status | org.bluetooth.service.phone_alert_status |
| 0x180F | Battery | org.bluetooth.service.battery_service |
| 0x1810 | Blood Pressure | org.bluetooth.service.blood_pressure |
| 0x1811 | Alert Notification | org.bluetooth.service.alert_notification |
| 0x1812 | Human Interface Device | org.bluetooth.service.human_interface_device |
| 0x1813 | Scan Parameters | org.bluetooth.service.scan_parameters |
| 0x1814 | Running Speed and Cadence | org.bluetooth.service.running_speed_and_cadence |
| 0x1815 | Automation IO | org.bluetooth.service.automation_io |
| 0x1816 | Cycling Speed and Cadence | org.bluetooth.service.cycling_speed_and_cadence |
| 0x1818 | Cycling Power | org.bluetooth.service.cycling_power |
| 0x1819 | Location and Navigation | org.bluetooth.service.location_and_navigation |
| 0x181A | Environmental Sensing | org.bluetooth.service.environmental_sensing |
| 0x181B | Body Composition | org.bluetooth.service.body_composition |
| 0x181C | User Data | org.bluetooth.service.user_data |
| 0x181D | Weight Scale | org.bluetooth.service.weight_scale |
| 0x181E | Bond Management | org.bluetooth.service.bond_management |
| 0x181F | Continuous Glucose Monitoring | org.bluetooth.service.continuous_glucose_monitoring |
| 0x1820 | Internet Protocol Support | org.bluetooth.service.internet_protocol_support |
| 0x1821 | Indoor Positioning | org.bluetooth.service.indoor_positioning |
| 0x1822 | Pulse Oximeter | org.bluetooth.service.pulse_oximeter |
| 0x1823 | HTTP Proxy | org.bluetooth.service.http_proxy |
| 0x1824 | Transport Discovery | org.bluetooth.service.transport_discovery |
| 0x1825 | Object Transfer | org.bluetooth.service.object_transfer |
| 0x1826 | Fitness Machine | org.bluetooth.service.fitness_machine |
| 0x1827 | Mesh Provisioning | org.bluetooth.service.mesh_provisioning |
| 0x1828 | Mesh Proxy | org.bluetooth.service.mesh_proxy |
| 0x1829 | Reconnection Configuration | org.bluetooth.service.reconnection_configuration |
| 0x183A | Insulin Delivery | org.bluetooth.service.insulin_delivery |
| 0x183B | Binary Sensor | org.bluetooth.service.binary_sensor |
| 0x183C | Emergency Configuration | org.bluetooth.service.emergency_configuration |
| 0x183D | Authorization Control | org.bluetooth.service.authorization_control |
| 0x183E | Physical Activity Monitor | org.bluetooth.service.physical_activity_monitor |
| 0x183F | Elapsed Time | org.bluetooth.service.elapsed_time |
| 0x1840 | Generic Health Sensor | org.bluetooth.service.generic_health_sensor |
| 0x1843 | Audio Input Control | org.bluetooth.service.audio_input_control |
| 0x1844 | Volume Control | org.bluetooth.service.volume_control |
| 0x1845 | Volume Offset Control | org.bluetooth.service.volume_offset |
| 0x1846 | Coordinated Set Identification | org.bluetooth.service.coordinated_set_identification |
| 0x1847 | Device Time | org.bluetooth.service.device_time |
| 0x1848 | Media Control | org.bluetooth.service.media_control |
| 0x1849 | Generic Media Control | org.bluetooth.service.generic_media_control |
| 0x184A | Constant Tone Extension | org.bluetooth.service.constant_tone_extension |
| 0x184B | Telephone Bearer | org.bluetooth.service.telephone_bearer |
| 0x184C | Generic Telephone Bearer | org.bluetooth.service.generic_telephone_bearer |
| 0x184D | Microphone Control | org.bluetooth.service.microphone_control |
| 0x184E | Audio Stream Control | org.bluetooth.service.audio_stream_control |
| 0x184F | Broadcast Audio Scan | org.bluetooth.service.broadcast_audio_scan |
| 0x1850 | Published Audio Capabilities | org.bluetooth.service.published_audio_capabilities |
| 0x1851 | Basic Audio Announcement | org.bluetooth.service.basic_audio_announcement |
| 0x1852 | Broadcast Audio Announcement | org.bluetooth.service.broadcast_audio_announcement |
| 0x1853 | Common Audio | org.bluetooth.service.common_audio |
| 0x1854 | Hearing Access | org.bluetooth.service.hearing_access |
| 0x1855 | Telephony and Media Audio | org.bluetooth.service.telephony_and_media_audio |
| 0x1856 | Public Broadcast Announcement | org.bluetooth.service.public_broadcast_announcement |
| 0x1857 | Electronic Shelf Label | org.bluetooth.service.electronic_shelf_label |
| 0x1858 | Gaming Audio | org.bluetooth.service.gaming_audio |
| 0x1859 | Mesh Proxy Solicitation | org.bluetooth.service.mesh_proxy_solicitation |
| 0x185A | Industrial Measurement Device | org.bluetooth.service.industrial_measurement_device |
| 0x185B | Ranging | org.bluetooth.service.ranging |
| 0x185C | HID ISO | org.bluetooth.service.hid_iso |
| 0x185D | Cookware | org.bluetooth.service.cookware |
| 0x185E | Voice Assistant | org.bluetooth.service.voice_assistant |
| 0x185F | Generic Voice Assistant | org.bluetooth.service.generic_voice_assistant |
| 0x1860 | Tire Pressure Monitoring System | org.bluetooth.service.tire_pressure_monitoring_system |

## 特征（Characteristics，0x2A00 起）

| UUID | 名称 | SIG 标识 |
|---|---|---|
| 0x2A00 | Device Name | org.bluetooth.characteristic.gap.device_name |
| 0x2A01 | Appearance | org.bluetooth.characteristic.gap.appearance |
| 0x2A02 | Peripheral Privacy Flag | org.bluetooth.characteristic.gap.peripheral_privacy_flag |
| 0x2A03 | Reconnection Address | org.bluetooth.characteristic.gap.reconnection_address |
| 0x2A04 | Peripheral Preferred Connection Parameters | org.bluetooth.characteristic.gap.peripheral_preferred_connection_parameters |
| 0x2A05 | Service Changed | org.bluetooth.characteristic.gatt.service_changed |
| 0x2A06 | Alert Level | org.bluetooth.characteristic.alert_level |
| 0x2A07 | Tx Power Level | org.bluetooth.characteristic.tx_power_level |
| 0x2A08 | Date Time | org.bluetooth.characteristic.date_time |
| 0x2A09 | Day of Week | org.bluetooth.characteristic.day_of_week |
| 0x2A0A | Day Date Time | org.bluetooth.characteristic.day_date_time |
| 0x2A0C | Exact Time 256 | org.bluetooth.characteristic.exact_time_256 |
| 0x2A0D | DST Offset | org.bluetooth.characteristic.dst_offset |
| 0x2A0E | Time Zone | org.bluetooth.characteristic.time_zone |
| 0x2A0F | Local Time Information | org.bluetooth.characteristic.local_time_information |
| 0x2A11 | Time with DST | org.bluetooth.characteristic.time_with_dst |
| 0x2A12 | Time Accuracy | org.bluetooth.characteristic.time_accuracy |
| 0x2A13 | Time Source | org.bluetooth.characteristic.time_source |
| 0x2A14 | Reference Time Information | org.bluetooth.characteristic.reference_time_information |
| 0x2A16 | Time Update Control Point | org.bluetooth.characteristic.time_update_control_point |
| 0x2A17 | Time Update State | org.bluetooth.characteristic.time_update_state |
| 0x2A18 | Glucose Measurement | org.bluetooth.characteristic.glucose_measurement |
| 0x2A19 | Battery Level | org.bluetooth.characteristic.battery_level |
| 0x2A1C | Temperature Measurement | org.bluetooth.characteristic.temperature_measurement |
| 0x2A1D | Temperature Type | org.bluetooth.characteristic.temperature_type |
| 0x2A1E | Intermediate Temperature | org.bluetooth.characteristic.intermediate_temperature |
| 0x2A21 | Measurement Interval | org.bluetooth.characteristic.measurement_interval |
| 0x2A22 | Boot Keyboard Input Report | org.bluetooth.characteristic.boot_keyboard_input_report |
| 0x2A23 | System ID | org.bluetooth.characteristic.system_id |
| 0x2A24 | Model Number String | org.bluetooth.characteristic.model_number_string |
| 0x2A25 | Serial Number String | org.bluetooth.characteristic.serial_number_string |
| 0x2A26 | Firmware Revision String | org.bluetooth.characteristic.firmware_revision_string |
| 0x2A27 | Hardware Revision String | org.bluetooth.characteristic.hardware_revision_string |
| 0x2A28 | Software Revision String | org.bluetooth.characteristic.software_revision_string |
| 0x2A29 | Manufacturer Name String | org.bluetooth.characteristic.manufacturer_name_string |
| 0x2A2A | IEEE 11073-20601 Regulatory Certification Data List | org.bluetooth.characteristic.ieee_11073_20601_regulatory_certification_data_list |
| 0x2A2B | Current Time | org.bluetooth.characteristic.current_time |
| 0x2A2C | Magnetic Declination | org.bluetooth.characteristic.magnetic_declination |
| 0x2A31 | Scan Refresh | org.bluetooth.characteristic.scan_refresh |
| 0x2A32 | Boot Keyboard Output Report | org.bluetooth.characteristic.boot_keyboard_output_report |
| 0x2A33 | Boot Mouse Input Report | org.bluetooth.characteristic.boot_mouse_input_report |
| 0x2A34 | Glucose Measurement Context | org.bluetooth.characteristic.glucose_measurement_context |
| 0x2A35 | Blood Pressure Measurement | org.bluetooth.characteristic.blood_pressure_measurement |
| 0x2A36 | Intermediate Cuff Pressure | org.bluetooth.characteristic.intermediate_cuff_pressure |
| 0x2A37 | Heart Rate Measurement | org.bluetooth.characteristic.heart_rate_measurement |
| 0x2A38 | Body Sensor Location | org.bluetooth.characteristic.body_sensor_location |
| 0x2A39 | Heart Rate Control Point | org.bluetooth.characteristic.heart_rate_control_point |
| 0x2A3F | Alert Status | org.bluetooth.characteristic.alert_status |
| 0x2A40 | Ringer Control Point | org.bluetooth.characteristic.ringer_control_point |
| 0x2A41 | Ringer Setting | org.bluetooth.characteristic.ringer_setting |
| 0x2A42 | Alert Category ID Bit Mask | org.bluetooth.characteristic.alert_category_id_bit_mask |
| 0x2A43 | Alert Category ID | org.bluetooth.characteristic.alert_category_id |
| 0x2A44 | Alert Notification Control Point | org.bluetooth.characteristic.alert_notification_control_point |
| 0x2A45 | Unread Alert Status | org.bluetooth.characteristic.unread_alert_status |
| 0x2A46 | New Alert | org.bluetooth.characteristic.new_alert |
| 0x2A47 | Supported New Alert Category | org.bluetooth.characteristic.supported_new_alert_category |
| 0x2A48 | Supported Unread Alert Category | org.bluetooth.characteristic.supported_unread_alert_category |
| 0x2A49 | Blood Pressure Feature | org.bluetooth.characteristic.blood_pressure_feature |
| 0x2A4A | HID Information | org.bluetooth.characteristic.hid_information |
| 0x2A4B | Report Map | org.bluetooth.characteristic.report_map |
| 0x2A4C | HID Control Point | org.bluetooth.characteristic.hid_control_point |
| 0x2A4D | Report | org.bluetooth.characteristic.report |
| 0x2A4E | Protocol Mode | org.bluetooth.characteristic.protocol_mode |
| 0x2A4F | Scan Interval Window | org.bluetooth.characteristic.scan_interval_window |
| 0x2A50 | PnP ID | org.bluetooth.characteristic.pnp_id |
| 0x2A51 | Glucose Feature | org.bluetooth.characteristic.glucose_feature |
| 0x2A52 | Record Access Control Point | org.bluetooth.characteristic.record_access_control_point |
| 0x2A53 | RSC Measurement | org.bluetooth.characteristic.rsc_measurement |
| 0x2A54 | RSC Feature | org.bluetooth.characteristic.rsc_feature |
| 0x2A55 | SC Control Point | org.bluetooth.characteristic.sc_control_point |
| 0x2A5A | Aggregate | org.bluetooth.characteristic.aggregate |
| 0x2A5B | CSC Measurement | org.bluetooth.characteristic.csc_measurement |
| 0x2A5C | CSC Feature | org.bluetooth.characteristic.csc_feature |
| 0x2A5D | Sensor Location | org.bluetooth.characteristic.sensor_location |
| 0x2A5E | PLX Spot-Check Measurement | org.bluetooth.characteristic.plx_spot_check_measurement |
| 0x2A5F | PLX Continuous Measurement | org.bluetooth.characteristic.plx_continuous_measurement |
| 0x2A60 | PLX Features | org.bluetooth.characteristic.plx_features |
| 0x2A63 | Cycling Power Measurement | org.bluetooth.characteristic.cycling_power_measurement |
| 0x2A64 | Cycling Power Vector | org.bluetooth.characteristic.cycling_power_vector |
| 0x2A65 | Cycling Power Feature | org.bluetooth.characteristic.cycling_power_feature |
| 0x2A66 | Cycling Power Control Point | org.bluetooth.characteristic.cycling_power_control_point |
| 0x2A67 | Location and Speed | org.bluetooth.characteristic.location_and_speed |
| 0x2A68 | Navigation | org.bluetooth.characteristic.navigation |
| 0x2A69 | Position Quality | org.bluetooth.characteristic.position_quality |
| 0x2A6A | LN Feature | org.bluetooth.characteristic.ln_feature |
| 0x2A6B | LN Control Point | org.bluetooth.characteristic.ln_control_point |
| 0x2A6C | Elevation | org.bluetooth.characteristic.elevation |
| 0x2A6D | Pressure | org.bluetooth.characteristic.pressure |
| 0x2A6E | Temperature | org.bluetooth.characteristic.temperature |
| 0x2A6F | Humidity | org.bluetooth.characteristic.humidity |
| 0x2A70 | True Wind Speed | org.bluetooth.characteristic.true_wind_speed |
| 0x2A71 | True Wind Direction | org.bluetooth.characteristic.true_wind_direction |
| 0x2A72 | Apparent Wind Speed | org.bluetooth.characteristic.apparent_wind_speed |
| 0x2A73 | Apparent Wind Direction | org.bluetooth.characteristic.apparent_wind_direction |
| 0x2A74 | Gust Factor | org.bluetooth.characteristic.gust_factor |
| 0x2A75 | Pollen Concentration | org.bluetooth.characteristic.pollen_concentration |
| 0x2A76 | UV Index | org.bluetooth.characteristic.uv_index |
| 0x2A77 | Irradiance | org.bluetooth.characteristic.irradiance |
| 0x2A78 | Rainfall | org.bluetooth.characteristic.rainfall |
| 0x2A79 | Wind Chill | org.bluetooth.characteristic.wind_chill |
| 0x2A7A | Heat Index | org.bluetooth.characteristic.heat_index |
| 0x2A7B | Dew Point | org.bluetooth.characteristic.dew_point |
| 0x2A7D | Descriptor Value Changed | org.bluetooth.characteristic.descriptor_value_changed |
| 0x2A7E | Aerobic Heart Rate Lower Limit | org.bluetooth.characteristic.aerobic_heart_rate_lower_limit |
| 0x2A7F | Aerobic Threshold | org.bluetooth.characteristic.aerobic_threshold |
| 0x2A80 | Age | org.bluetooth.characteristic.age |
| 0x2A81 | Anaerobic Heart Rate Lower Limit | org.bluetooth.characteristic.anaerobic_heart_rate_lower_limit |
| 0x2A82 | Anaerobic Heart Rate Upper Limit | org.bluetooth.characteristic.anaerobic_heart_rate_upper_limit |
| 0x2A83 | Anaerobic Threshold | org.bluetooth.characteristic.anaerobic_threshold |
| 0x2A84 | Aerobic Heart Rate Upper Limit | org.bluetooth.characteristic.aerobic_heart_rate_upper_limit |
| 0x2A85 | Date of Birth | org.bluetooth.characteristic.date_of_birth |
| 0x2A86 | Date of Threshold Assessment | org.bluetooth.characteristic.date_of_threshold_assessment |
| 0x2A87 | Email Address | org.bluetooth.characteristic.email_address |
| 0x2A88 | Fat Burn Heart Rate Lower Limit | org.bluetooth.characteristic.fat_burn_heart_rate_lower_limit |
| 0x2A89 | Fat Burn Heart Rate Upper Limit | org.bluetooth.characteristic.fat_burn_heart_rate_upper_limit |
| 0x2A8A | First Name | org.bluetooth.characteristic.first_name |
| 0x2A8B | Five Zone Heart Rate Limits | org.bluetooth.characteristic.five_zone_heart_rate_limits |
| 0x2A8C | Gender | org.bluetooth.characteristic.gender |
| 0x2A8D | Heart Rate Max | org.bluetooth.characteristic.heart_rate_max |
| 0x2A8E | Height | org.bluetooth.characteristic.height |
| 0x2A8F | Hip Circumference | org.bluetooth.characteristic.hip_circumference |
| 0x2A90 | Last Name | org.bluetooth.characteristic.last_name |
| 0x2A91 | Maximum Recommended Heart Rate | org.bluetooth.characteristic.maximum_recommended_heart_rate |
| 0x2A92 | Resting Heart Rate | org.bluetooth.characteristic.resting_heart_rate |
| 0x2A93 | Sport Type for Aerobic and Anaerobic Thresholds | org.bluetooth.characteristic.sport_type_for_aerobic_and_anaerobic_thresholds |
| 0x2A94 | Three Zone Heart Rate Limits | org.bluetooth.characteristic.three_zone_heart_rate_limits |
| 0x2A95 | Two Zone Heart Rate Limits | org.bluetooth.characteristic.two_zone_heart_rate_limits |
| 0x2A96 | VO2 Max | org.bluetooth.characteristic.vo2_max |
| 0x2A97 | Waist Circumference | org.bluetooth.characteristic.waist_circumference |
| 0x2A98 | Weight | org.bluetooth.characteristic.weight |
| 0x2A99 | Database Change Increment | org.bluetooth.characteristic.database_change_increment |
| 0x2A9A | User Index | org.bluetooth.characteristic.user_index |
| 0x2A9B | Body Composition Feature | org.bluetooth.characteristic.body_composition_feature |
| 0x2A9C | Body Composition Measurement | org.bluetooth.characteristic.body_composition_measurement |
| 0x2A9D | Weight Measurement | org.bluetooth.characteristic.weight_measurement |
| 0x2A9E | Weight Scale Feature | org.bluetooth.characteristic.weight_scale_feature |
| 0x2A9F | User Control Point | org.bluetooth.characteristic.user_control_point |
| 0x2AA0 | Magnetic Flux Density - 2D | org.bluetooth.characteristic.magnetic_flux_density_2d |
| 0x2AA1 | Magnetic Flux Density - 3D | org.bluetooth.characteristic.magnetic_flux_density_3d |
| 0x2AA2 | Language | org.bluetooth.characteristic.language |
| 0x2AA3 | Barometric Pressure Trend | org.bluetooth.characteristic.barometric_pressure_trend |
| 0x2AA4 | Bond Management Control Point | org.bluetooth.characteristic.bond_management_control_point |
| 0x2AA5 | Bond Management Feature | org.bluetooth.characteristic.bond_management_feature |
| 0x2AA6 | Central Address Resolution | org.bluetooth.characteristic.gap.central_address_resolution |
| 0x2AA7 | CGM Measurement | org.bluetooth.characteristic.cgm_measurement |
| 0x2AA8 | CGM Feature | org.bluetooth.characteristic.cgm_feature |
| 0x2AA9 | CGM Status | org.bluetooth.characteristic.cgm_status |
| 0x2AAA | CGM Session Start Time | org.bluetooth.characteristic.cgm_session_start_time |
| 0x2AAB | CGM Session Run Time | org.bluetooth.characteristic.cgm_session_run_time |
| 0x2AAC | CGM Specific Ops Control Point | org.bluetooth.characteristic.cgm_specific_ops_control_point |
| 0x2AAD | Indoor Positioning Configuration | org.bluetooth.characteristic.indoor_positioning_configuration |
| 0x2AAE | Latitude | org.bluetooth.characteristic.latitude |
| 0x2AAF | Longitude | org.bluetooth.characteristic.longitude |
| 0x2AB0 | Local North Coordinate | org.bluetooth.characteristic.local_north_coordinate |
| 0x2AB1 | Local East Coordinate | org.bluetooth.characteristic.local_east_coordinate |
| 0x2AB2 | Floor Number | org.bluetooth.characteristic.floor_number |
| 0x2AB3 | Altitude | org.bluetooth.characteristic.altitude |
| 0x2AB4 | Uncertainty | org.bluetooth.characteristic.uncertainty |
| 0x2AB5 | Location Name | org.bluetooth.characteristic.location_name |
| 0x2AB6 | URI | org.bluetooth.characteristic.uri |
| 0x2AB7 | HTTP Headers | org.bluetooth.characteristic.http_headers |
| 0x2AB8 | HTTP Status Code | org.bluetooth.characteristic.http_status_code |
| 0x2AB9 | HTTP Entity Body | org.bluetooth.characteristic.http_entity_body |
| 0x2ABA | HTTP Control Point | org.bluetooth.characteristic.http_control_point |
| 0x2ABB | HTTPS Security | org.bluetooth.characteristic.https_security |
| 0x2ABC | TDS Control Point | org.bluetooth.characteristic.tds_control_point |
| 0x2ABD | OTS Feature | org.bluetooth.characteristic.ots_feature |
| 0x2ABE | Object Name | org.bluetooth.characteristic.object_name |
| 0x2ABF | Object Type | org.bluetooth.characteristic.object_type |
| 0x2AC0 | Object Size | org.bluetooth.characteristic.object_size |
| 0x2AC1 | Object First-Created | org.bluetooth.characteristic.object_first_created |
| 0x2AC2 | Object Last-Modified | org.bluetooth.characteristic.object_last_modified |
| 0x2AC3 | Object ID | org.bluetooth.characteristic.object_id |
| 0x2AC4 | Object Properties | org.bluetooth.characteristic.object_properties |
| 0x2AC5 | Object Action Control Point | org.bluetooth.characteristic.object_action_control_point |
| 0x2AC6 | Object List Control Point | org.bluetooth.characteristic.object_list_control_point |
| 0x2AC7 | Object List Filter | org.bluetooth.characteristic.object_list_filter |
| 0x2AC8 | Object Changed | org.bluetooth.characteristic.object_changed |
| 0x2AC9 | Resolvable Private Address Only | org.bluetooth.characteristic.resolvable_private_address_only |
| 0x2ACC | Fitness Machine Feature | org.bluetooth.characteristic.fitness_machine_feature |
| 0x2ACD | Treadmill Data | org.bluetooth.characteristic.treadmill_data |
| 0x2ACE | Cross Trainer Data | org.bluetooth.characteristic.cross_trainer_data |
| 0x2ACF | Step Climber Data | org.bluetooth.characteristic.step_climber_data |
| 0x2AD0 | Stair Climber Data | org.bluetooth.characteristic.stair_climber_data |
| 0x2AD1 | Rower Data | org.bluetooth.characteristic.rower_data |
| 0x2AD2 | Indoor Bike Data | org.bluetooth.characteristic.indoor_bike_data |
| 0x2AD3 | Training Status | org.bluetooth.characteristic.training_status |
| 0x2AD4 | Supported Speed Range | org.bluetooth.characteristic.supported_speed_range |
| 0x2AD5 | Supported Inclination Range | org.bluetooth.characteristic.supported_inclination_range |
| 0x2AD6 | Supported Resistance Level Range | org.bluetooth.characteristic.supported_resistance_level_range |
| 0x2AD7 | Supported Heart Rate Range | org.bluetooth.characteristic.supported_heart_rate_range |
| 0x2AD8 | Supported Power Range | org.bluetooth.characteristic.supported_power_range |
| 0x2AD9 | Fitness Machine Control Point | org.bluetooth.characteristic.fitness_machine_control_point |
| 0x2ADA | Fitness Machine Status | org.bluetooth.characteristic.fitness_machine_status |
| 0x2ADB | Mesh Provisioning Data In | org.bluetooth.characteristic.mesh_provisioning_data_in |
| 0x2ADC | Mesh Provisioning Data Out | org.bluetooth.characteristic.mesh_provisioning_data_out |
| 0x2ADD | Mesh Proxy Data In | org.bluetooth.characteristic.mesh_proxy_data_in |
| 0x2ADE | Mesh Proxy Data Out | org.bluetooth.characteristic.mesh_proxy_data_out |
| 0x2AE0 | Average Current | org.bluetooth.characteristic.average_current |
| 0x2AE1 | Average Voltage | org.bluetooth.characteristic.average_voltage |
| 0x2AE2 | Boolean | org.bluetooth.characteristic.boolean |
| 0x2AE3 | Chromatic Distance from Planckian | org.bluetooth.characteristic.chromatic_distance_from_planckian |
| 0x2AE4 | Chromaticity Coordinates | org.bluetooth.characteristic.chromaticity_coordinates |
| 0x2AE5 | Chromaticity in CCT and Duv Values | org.bluetooth.characteristic.chromaticity_in_cct_and_duv_values |
| 0x2AE6 | Chromaticity Tolerance | org.bluetooth.characteristic.chromaticity_tolerance |
| 0x2AE7 | CIE 13.3-1995 Color Rendering Index | org.bluetooth.characteristic.cie_13_3_1995_color_rendering_index |
| 0x2AE8 | Coefficient | org.bluetooth.characteristic.coefficient |
| 0x2AE9 | Correlated Color Temperature | org.bluetooth.characteristic.correlated_color_temperature |
| 0x2AEA | Count 16 | org.bluetooth.characteristic.count_16 |
| 0x2AEB | Count 24 | org.bluetooth.characteristic.count_24 |
| 0x2AEC | Country Code | org.bluetooth.characteristic.country_code |
| 0x2AED | Date UTC | org.bluetooth.characteristic.date_utc |
| 0x2AEE | Electric Current | org.bluetooth.characteristic.electric_current |
| 0x2AEF | Electric Current Range | org.bluetooth.characteristic.electric_current_range |
| 0x2AF0 | Electric Current Specification | org.bluetooth.characteristic.electric_current_specification |
| 0x2AF1 | Electric Current Statistics | org.bluetooth.characteristic.electric_current_statistics |
| 0x2AF2 | Energy | org.bluetooth.characteristic.energy |
| 0x2AF3 | Energy in a Period of Day | org.bluetooth.characteristic.energy_in_a_period_of_day |
| 0x2AF4 | Event Statistics | org.bluetooth.characteristic.event_statistics |
| 0x2AF5 | Fixed String 16 | org.bluetooth.characteristic.fixed_string_16 |
| 0x2AF6 | Fixed String 24 | org.bluetooth.characteristic.fixed_string_24 |
| 0x2AF7 | Fixed String 36 | org.bluetooth.characteristic.fixed_string_36 |
| 0x2AF8 | Fixed String 8 | org.bluetooth.characteristic.fixed_string_8 |
| 0x2AF9 | Generic Level | org.bluetooth.characteristic.generic_level |
| 0x2AFA | Global Trade Item Number | org.bluetooth.characteristic.global_trade_item_number |
| 0x2AFB | Illuminance | org.bluetooth.characteristic.illuminance |
| 0x2AFC | Luminous Efficacy | org.bluetooth.characteristic.luminous_efficacy |
| 0x2AFD | Luminous Energy | org.bluetooth.characteristic.luminous_energy |
| 0x2AFE | Luminous Exposure | org.bluetooth.characteristic.luminous_exposure |
| 0x2AFF | Luminous Flux | org.bluetooth.characteristic.luminous_flux |
| 0x2B00 | Luminous Flux Range | org.bluetooth.characteristic.luminous_flux_range |
| 0x2B01 | Luminous Intensity | org.bluetooth.characteristic.luminous_intensity |
| 0x2B02 | Mass Flow | org.bluetooth.characteristic.mass_flow |
| 0x2B03 | Perceived Lightness | org.bluetooth.characteristic.perceived_lightness |
| 0x2B04 | Percentage 8 | org.bluetooth.characteristic.percentage_8 |
| 0x2B05 | Power | org.bluetooth.characteristic.power |
| 0x2B06 | Power Specification | org.bluetooth.characteristic.power_specification |
| 0x2B07 | Relative Runtime in a Current Range | org.bluetooth.characteristic.relative_runtime_in_a_current_range |
| 0x2B08 | Relative Runtime in a Generic Level Range | org.bluetooth.characteristic.relative_runtime_in_a_generic_level_range |
| 0x2B09 | Relative Value in a Voltage Range | org.bluetooth.characteristic.relative_value_in_a_voltage_range |
| 0x2B0A | Relative Value in an Illuminance Range | org.bluetooth.characteristic.relative_value_in_an_illuminance_range |
| 0x2B0B | Relative Value in a Period of Day | org.bluetooth.characteristic.relative_value_in_a_period_of_day |
| 0x2B0C | Relative Value in a Temperature Range | org.bluetooth.characteristic.relative_value_in_a_temperature_range |
| 0x2B0D | Temperature 8 | org.bluetooth.characteristic.temperature_8 |
| 0x2B0E | Temperature 8 in a Period of Day | org.bluetooth.characteristic.temperature_8_in_a_period_of_day |
| 0x2B0F | Temperature 8 Statistics | org.bluetooth.characteristic.temperature_8_statistics |
| 0x2B10 | Temperature Range | org.bluetooth.characteristic.temperature_range |
| 0x2B11 | Temperature Statistics | org.bluetooth.characteristic.temperature_statistics |
| 0x2B12 | Time Decihour 8 | org.bluetooth.characteristic.time_decihour_8 |
| 0x2B13 | Time Exponential 8 | org.bluetooth.characteristic.time_exponential_8 |
| 0x2B14 | Time Hour 24 | org.bluetooth.characteristic.time_hour_24 |
| 0x2B15 | Time Millisecond 24 | org.bluetooth.characteristic.time_millisecond_24 |
| 0x2B16 | Time Second 16 | org.bluetooth.characteristic.time_second_16 |
| 0x2B17 | Time Second 8 | org.bluetooth.characteristic.time_second_8 |
| 0x2B18 | Voltage | org.bluetooth.characteristic.voltage |
| 0x2B19 | Voltage Specification | org.bluetooth.characteristic.voltage_specification |
| 0x2B1A | Voltage Statistics | org.bluetooth.characteristic.voltage_statistics |
| 0x2B1B | Volume Flow | org.bluetooth.characteristic.volume_flow |
| 0x2B1C | Chromaticity Coordinate | org.bluetooth.characteristic.chromaticity_coordinate |
| 0x2B1D | RC Feature | org.bluetooth.characteristic.rc_feature |
| 0x2B1E | RC Settings | org.bluetooth.characteristic.rc_settings |
| 0x2B1F | Reconnection Configuration Control Point | org.bluetooth.characteristic.reconnection_configuration_control_point |
| 0x2B20 | IDD Status Changed | org.bluetooth.characteristic.idd_status_changed |
| 0x2B21 | IDD Status | org.bluetooth.characteristic.idd_status |
| 0x2B22 | IDD Annunciation Status | org.bluetooth.characteristic.idd_annunciation_status |
| 0x2B23 | IDD Features | org.bluetooth.characteristic.idd_features |
| 0x2B24 | IDD Status Reader Control Point | org.bluetooth.characteristic.idd_status_reader_control_point |
| 0x2B25 | IDD Command Control Point | org.bluetooth.characteristic.idd_command_control_point |
| 0x2B26 | IDD Command Data | org.bluetooth.characteristic.idd_command_data |
| 0x2B27 | IDD Record Access Control Point | org.bluetooth.characteristic.idd_record_access_control_point |
| 0x2B28 | IDD History Data | org.bluetooth.characteristic.idd_history_data |
| 0x2B29 | Client Supported Features | org.bluetooth.characteristic.client_supported_features |
| 0x2B2A | Database Hash | org.bluetooth.characteristic.database_hash |
| 0x2B2B | BSS Control Point | org.bluetooth.characteristic.bss_control_point |
| 0x2B2C | BSS Response | org.bluetooth.characteristic.bss_response |
| 0x2B2D | Emergency ID | org.bluetooth.characteristic.emergency_id |
| 0x2B2E | Emergency Text | org.bluetooth.characteristic.emergency_text |
| 0x2B2F | ACS Status | org.bluetooth.characteristic.acs_status |
| 0x2B30 | ACS Data In | org.bluetooth.characteristic.acs_data_in |
| 0x2B31 | ACS Data Out Notify | org.bluetooth.characteristic.acs_data_out_notify |
| 0x2B32 | ACS Data Out Indicate | org.bluetooth.characteristic.acs_data_out_indicate |
| 0x2B33 | ACS Control Point | org.bluetooth.characteristic.acs_control_point |
| 0x2B34 | Enhanced Blood Pressure Measurement | org.bluetooth.characteristic.enhanced_blood_pressure_measurement |
| 0x2B35 | Enhanced Intermediate Cuff Pressure | org.bluetooth.characteristic.enhanced_intermediate_cuff_pressure |
| 0x2B36 | Blood Pressure Record | org.bluetooth.characteristic.blood_pressure_record |
| 0x2B37 | Registered User | org.bluetooth.characteristic.registered_user |
| 0x2B38 | BR-EDR Handover Data | org.bluetooth.characteristic.br_edr_handover_data |
| 0x2B39 | Bluetooth SIG Data | org.bluetooth.characteristic.bluetooth_sig_data |
| 0x2B3A | Server Supported Features | org.bluetooth.characteristic.server_supported_features |
| 0x2B3B | Physical Activity Monitor Features | org.bluetooth.characteristic.physical_activity_monitor_features |
| 0x2B3C | General Activity Instantaneous Data | org.bluetooth.characteristic.general_activity_instantaneous_data |
| 0x2B3D | General Activity Summary Data | org.bluetooth.characteristic.general_activity_summary_data |
| 0x2B3E | CardioRespiratory Activity Instantaneous Data | org.bluetooth.characteristic.cardiorespiratory_activity_instantaneous_data |
| 0x2B3F | CardioRespiratory Activity Summary Data | org.bluetooth.characteristic.cardiorespiratory_activity_summary_data |
| 0x2B40 | Step Counter Activity Summary Data | org.bluetooth.characteristic.step_counter_activity_summary_data |
| 0x2B41 | Sleep Activity Instantaneous Data | org.bluetooth.characteristic.sleep_activity_instantaneous_data |
| 0x2B42 | Sleep Activity Summary Data | org.bluetooth.characteristic.sleep_activity_summary_data |
| 0x2B43 | Physical Activity Monitor Control Point | org.bluetooth.characteristic.physical_activity_monitor_control_point |
| 0x2B44 | Physical Activity Current Session | org.bluetooth.characteristic.physical_activity_current_session |
| 0x2B45 | Physical Activity Session Descriptor | org.bluetooth.characteristic.physical_activity_session_descriptor |
| 0x2B46 | Preferred Units | org.bluetooth.characteristic.preferred_units |
| 0x2B47 | High Resolution Height | org.bluetooth.characteristic.high_resolution_height |
| 0x2B48 | Middle Name | org.bluetooth.characteristic.middle_name |
| 0x2B49 | Stride Length | org.bluetooth.characteristic.stride_length |
| 0x2B4A | Handedness | org.bluetooth.characteristic.handedness |
| 0x2B4B | Device Wearing Position | org.bluetooth.characteristic.device_wearing_position |
| 0x2B4C | Four Zone Heart Rate Limits | org.bluetooth.characteristic.four_zone_heart_rate_limits |
| 0x2B4D | High Intensity Exercise Threshold | org.bluetooth.characteristic.high_intensity_exercise_threshold |
| 0x2B4E | Activity Goal | org.bluetooth.characteristic.activity_goal |
| 0x2B4F | Sedentary Interval Notification | org.bluetooth.characteristic.sedentary_interval_notification |
| 0x2B50 | Caloric Intake | org.bluetooth.characteristic.caloric_intake |
| 0x2B51 | TMAP Role | org.bluetooth.characteristic.tmap_role |
| 0x2B77 | Audio Input State | org.bluetooth.characteristic.audio_input_state |
| 0x2B78 | Gain Settings Attribute | org.bluetooth.characteristic.gain_settings_attribute |
| 0x2B79 | Audio Input Type | org.bluetooth.characteristic.audio_input_type |
| 0x2B7A | Audio Input Status | org.bluetooth.characteristic.audio_input_status |
| 0x2B7B | Audio Input Control Point | org.bluetooth.characteristic.audio_input_control_point |
| 0x2B7C | Audio Input Description | org.bluetooth.characteristic.audio_input_description |
| 0x2B7D | Volume State | org.bluetooth.characteristic.volume_state |
| 0x2B7E | Volume Control Point | org.bluetooth.characteristic.volume_control_point |
| 0x2B7F | Volume Flags | org.bluetooth.characteristic.volume_flags |
| 0x2B80 | Volume Offset State | org.bluetooth.characteristic.volume_offset_state |
| 0x2B81 | Audio Location | org.bluetooth.characteristic.audio_location |
| 0x2B82 | Volume Offset Control Point | org.bluetooth.characteristic.volume_offset_control_point |
| 0x2B83 | Audio Output Description | org.bluetooth.characteristic.audio_output_description |
| 0x2B84 | Set Identity Resolving Key | org.bluetooth.characteristic.set_identity_resolving_key |
| 0x2B85 | Coordinated Set Size | org.bluetooth.characteristic.size_characteristic |
| 0x2B86 | Set Member Lock | org.bluetooth.characteristic.lock_characteristic |
| 0x2B87 | Set Member Rank | org.bluetooth.characteristic.rank_characteristic |
| 0x2B88 | Encrypted Data Key Material | org.bluetooth.characteristic.encrypted_data_key_material |
| 0x2B89 | Apparent Energy 32 | org.bluetooth.characteristic.apparent_energy_32 |
| 0x2B8A | Apparent Power | org.bluetooth.characteristic.apparent_power |
| 0x2B8B | Live Health Observations | org.bluetooth.characteristic.live_health_observations |
| 0x2B8C | "CO\\textsubscript{2} Concentration" | org.bluetooth.characteristic.co2_concentration |
| 0x2B8D | Cosine of the Angle | org.bluetooth.characteristic.cosine_of_the_angle |
| 0x2B8E | Device Time Feature | org.bluetooth.characteristic.device_time_feature |
| 0x2B8F | Device Time Parameters | org.bluetooth.characteristic.device_time_parameters |
| 0x2B90 | Device Time | org.bluetooth.characteristic.device_time |
| 0x2B91 | Device Time Control Point | org.bluetooth.characteristic.device_time_control_point |
| 0x2B92 | Time Change Log Data | org.bluetooth.characteristic.time_change_log_data |
| 0x2B93 | Media Player Name | org.bluetooth.characteristic.media_player_name |
| 0x2B94 | Media Player Icon Object ID | org.bluetooth.characteristic.media_player_icon_object_id |
| 0x2B95 | Media Player Icon URL | org.bluetooth.characteristic.media_player_icon_url |
| 0x2B96 | Track Changed | org.bluetooth.characteristic.track_changed |
| 0x2B97 | Track Title | org.bluetooth.characteristic.track_title |
| 0x2B98 | Track Duration | org.bluetooth.characteristic.track_duration |
| 0x2B99 | Track Position | org.bluetooth.characteristic.track_position |
| 0x2B9A | Playback Speed | org.bluetooth.characteristic.playback_speed |
| 0x2B9B | Seeking Speed | org.bluetooth.characteristic.seeking_speed |
| 0x2B9C | Current Track Segments Object ID | org.bluetooth.characteristic.current_track_segments_object_id |
| 0x2B9D | Current Track Object ID | org.bluetooth.characteristic.current_track_object_id |
| 0x2B9E | Next Track Object ID | org.bluetooth.characteristic.next_track_object_id |
| 0x2B9F | Parent Group Object ID | org.bluetooth.characteristic.parent_group_object_id |
| 0x2BA0 | Current Group Object ID | org.bluetooth.characteristic.current_group_object_id |
| 0x2BA1 | Playing Order | org.bluetooth.characteristic.playing_order |
| 0x2BA2 | Playing Orders Supported | org.bluetooth.characteristic.playing_orders_supported |
| 0x2BA3 | Media State | org.bluetooth.characteristic.media_state |
| 0x2BA4 | Media Control Point | org.bluetooth.characteristic.media_control_point |
| 0x2BA5 | Media Control Point Opcodes Supported | org.bluetooth.characteristic.media_control_point_opcodes_supported |
| 0x2BA6 | Search Results Object ID | org.bluetooth.characteristic.search_results_object_id |
| 0x2BA7 | Search Control Point | org.bluetooth.characteristic.search_control_point |
| 0x2BA8 | Energy 32 | org.bluetooth.characteristic.energy_32 |
| 0x2BAD | Constant Tone Extension Enable | org.bluetooth.characteristic.constant_tone_extension_enable |
| 0x2BAE | Advertising Constant Tone Extension Minimum Length | org.bluetooth.characteristic.advertising_constant_tone_extension_minimum_length |
| 0x2BAF | Advertising Constant Tone Extension Minimum Transmit Count | org.bluetooth.characteristic.advertising_constant_tone_extension_minimum_transmit_count |
| 0x2BB0 | Advertising Constant Tone Extension Transmit Duration | org.bluetooth.characteristic.advertising_constant_tone_extension_transmit_duration |
| 0x2BB1 | Advertising Constant Tone Extension Interval | org.bluetooth.characteristic.advertising_constant_tone_extension_interval |
| 0x2BB2 | Advertising Constant Tone Extension PHY | org.bluetooth.characteristic.advertising_constant_tone_extension_phy |
| 0x2BB3 | Bearer Provider Name | org.bluetooth.characteristic.bearer_provider_name |
| 0x2BB4 | Bearer UCI | org.bluetooth.characteristic.bearer_uci |
| 0x2BB5 | Bearer Technology | org.bluetooth.characteristic.bearer_technology |
| 0x2BB6 | Bearer URI Schemes Supported List | org.bluetooth.characteristic.bearer_uri_schemes_supported_list |
| 0x2BB7 | Bearer Signal Strength | org.bluetooth.characteristic.bearer_signal_strength |
| 0x2BB8 | Bearer Signal Strength Reporting Interval | org.bluetooth.characteristic.bearer_signal_strength_reporting_interval |
| 0x2BB9 | Bearer List Current Calls | org.bluetooth.characteristic.bearer_list_current_calls |
| 0x2BBA | Content Control ID | org.bluetooth.characteristic.content_control_id |
| 0x2BBB | Status Flags | org.bluetooth.characteristic.status_flags |
| 0x2BBC | Incoming Call Target Bearer URI | org.bluetooth.characteristic.incoming_call_target_bearer_uri |
| 0x2BBD | Call State | org.bluetooth.characteristic.call_state |
| 0x2BBE | Call Control Point | org.bluetooth.characteristic.call_control_point |
| 0x2BBF | Call Control Point Optional Opcodes | org.bluetooth.characteristic.call_control_point_optional_opcodes |
| 0x2BC0 | Termination Reason | org.bluetooth.characteristic.termination_reason |
| 0x2BC1 | Incoming Call | org.bluetooth.characteristic.incoming_call |
| 0x2BC2 | Call Friendly Name | org.bluetooth.characteristic.call_friendly_name |
| 0x2BC3 | Mute | org.bluetooth.characteristic.mute |
| 0x2BC4 | Sink ASE | org.bluetooth.characteristic.sink_ase |
| 0x2BC5 | Source ASE | org.bluetooth.characteristic.source_ase |
| 0x2BC6 | ASE Control Point | org.bluetooth.characteristic.ase_control_point |
| 0x2BC7 | Broadcast Audio Scan Control Point | org.bluetooth.characteristic.broadcast_audio_scan_control_point |
| 0x2BC8 | Broadcast Receive State | org.bluetooth.characteristic.broadcast_receive_state |
| 0x2BC9 | Sink PAC | org.bluetooth.characteristic.sink_pac |
| 0x2BCA | Sink Audio Locations | org.bluetooth.characteristic.sink_audio_locations |
| 0x2BCB | Source PAC | org.bluetooth.characteristic.source_pac |
| 0x2BCC | Source Audio Locations | org.bluetooth.characteristic.source_audio_locations |
| 0x2BCD | Available Audio Contexts | org.bluetooth.characteristic.available_audio_contexts |
| 0x2BCE | Supported Audio Contexts | org.bluetooth.characteristic.supported_audio_contexts |
| 0x2BCF | Ammonia Concentration | org.bluetooth.characteristic.ammonia_concentration |
| 0x2BD0 | Carbon Monoxide Concentration | org.bluetooth.characteristic.carbon_monoxide_concentration |
| 0x2BD1 | Methane Concentration | org.bluetooth.characteristic.methane_concentration |
| 0x2BD2 | Nitrogen Dioxide Concentration | org.bluetooth.characteristic.nitrogen_dioxide_concentration |
| 0x2BD3 | Non-Methane Volatile Organic Compounds Concentration | org.bluetooth.characteristic.non-methane_volatile_organic_compounds_concentration |
| 0x2BD4 | Ozone Concentration | org.bluetooth.characteristic.ozone_concentration |
| 0x2BD5 | Particulate Matter - PM1 Concentration | org.bluetooth.characteristic.particulate_matter_pm1_concentration |
| 0x2BD6 | Particulate Matter - PM2.5 Concentration | org.bluetooth.characteristic.particulate_matter_pm2_5_concentration |
| 0x2BD7 | Particulate Matter - PM10 Concentration | org.bluetooth.characteristic.particulate_matter_pm10_concentration |
| 0x2BD8 | Sulfur Dioxide Concentration | org.bluetooth.characteristic.sulfur_dioxide_concentration |
| 0x2BD9 | Sulfur Hexafluoride Concentration | org.bluetooth.characteristic.sulfur_hexafluoride_concentration |
| 0x2BDA | Hearing Aid Features | org.bluetooth.characteristic.hearing_aid_features |
| 0x2BDB | Hearing Aid Preset Control Point | org.bluetooth.characteristic.hearing_aid_preset_control_point |
| 0x2BDC | Active Preset Index | org.bluetooth.characteristic.active_preset_index |
| 0x2BDD | Stored Health Observations | org.bluetooth.characteristic.stored_health_observations |
| 0x2BDE | Fixed String 64 | org.bluetooth.characteristic.fixed_string_64 |
| 0x2BDF | High Temperature | org.bluetooth.characteristic.high_temperature |
| 0x2BE0 | High Voltage | org.bluetooth.characteristic.high_voltage |
| 0x2BE1 | Light Distribution | org.bluetooth.characteristic.light_distribution |
| 0x2BE2 | Light Output | org.bluetooth.characteristic.light_output |
| 0x2BE3 | Light Source Type | org.bluetooth.characteristic.light_source_type |
| 0x2BE4 | Noise | org.bluetooth.characteristic.noise |
| 0x2BE5 | Relative Runtime in a Correlated Color Temperature Range | org.bluetooth.characteristic.relative_runtime_in_a_correlated_color_temperature_range |
| 0x2BE6 | Time Second 32 | org.bluetooth.characteristic.time_second_32 |
| 0x2BE7 | VOC Concentration | org.bluetooth.characteristic.voc_concentration |
| 0x2BE8 | Voltage Frequency | org.bluetooth.characteristic.voltage_frequency |
| 0x2BE9 | Battery Critical Status | org.bluetooth.characteristic.battery_critical_status |
| 0x2BEA | Battery Health Status | org.bluetooth.characteristic.battery_health_status |
| 0x2BEB | Battery Health Information | org.bluetooth.characteristic.battery_health_information |
| 0x2BEC | Battery Information | org.bluetooth.characteristic.battery_information |
| 0x2BED | Battery Level Status | org.bluetooth.characteristic.battery_level_status |
| 0x2BEE | Battery Time Status | org.bluetooth.characteristic.battery_time_status |
| 0x2BEF | Estimated Service Date | org.bluetooth.characteristic.estimated_service_date |
| 0x2BF0 | Battery Energy Status | org.bluetooth.characteristic.battery_energy_status |
| 0x2BF1 | Observation Schedule Changed | org.bluetooth.characteristic.observation_schedule_changed |
| 0x2BF2 | Elapsed Time | org.bluetooth.characteristic.elapsed_time |
| 0x2BF3 | Health Sensor Features | org.bluetooth.characteristic.health_sensor_features |
| 0x2BF4 | GHS Control Point | org.bluetooth.characteristic.ghs_control_point |
| 0x2BF5 | LE GATT Security Levels | org.bluetooth.characteristic.le_gatt_security_levels |
| 0x2BF6 | ESL Address | org.bluetooth.characteristic.esl_address |
| 0x2BF7 | AP Sync Key Material | org.bluetooth.characteristic.ap_sync_key_material |
| 0x2BF8 | ESL Response Key Material | org.bluetooth.characteristic.esl_response_key_material |
| 0x2BF9 | ESL Current Absolute Time | org.bluetooth.characteristic.esl_current_absolute_time |
| 0x2BFA | ESL Display Information | org.bluetooth.characteristic.esl_display_information |
| 0x2BFB | ESL Image Information | org.bluetooth.characteristic.esl_image_information |
| 0x2BFC | ESL Sensor Information | org.bluetooth.characteristic.esl_sensor_information |
| 0x2BFD | ESL LED Information | org.bluetooth.characteristic.esl_led_information |
| 0x2BFE | ESL Control Point | org.bluetooth.characteristic.esl_control_point |
| 0x2BFF | UDI for Medical Devices | org.bluetooth.characteristic.udi_for_medical_devices |
| 0x2C00 | GMAP Role | org.bluetooth.characteristic.gmap_role |
| 0x2C01 | UGG Features | org.bluetooth.characteristic.ugg_features |
| 0x2C02 | UGT Features | org.bluetooth.characteristic.ugt_features |
| 0x2C03 | BGS Features | org.bluetooth.characteristic.bgs_features |
| 0x2C04 | BGR Features | org.bluetooth.characteristic.bgr_features |
| 0x2C05 | Percentage 8 Steps | org.bluetooth.characteristic.percentage_8_steps |
| 0x2C06 | Acceleration | org.bluetooth.characteristic.acceleration |
| 0x2C07 | Force | org.bluetooth.characteristic.force |
| 0x2C08 | Linear Position | org.bluetooth.characteristic.linear_position |
| 0x2C09 | Rotational Speed | org.bluetooth.characteristic.rotational_speed |
| 0x2C0A | Length | org.bluetooth.characteristic.length |
| 0x2C0B | Torque | org.bluetooth.characteristic.torque |
| 0x2C0C | IMD Status | org.bluetooth.characteristic.imd_status |
| 0x2C0D | IMDS Descriptor Value Changed | org.bluetooth.characteristic.imds_descriptor_value_changed |
| 0x2C0E | First Use Date | org.bluetooth.characteristic.first_use_date |
| 0x2C0F | Life Cycle Data | org.bluetooth.characteristic.life_cycle_data |
| 0x2C10 | Work Cycle Data | org.bluetooth.characteristic.work_cycle_data |
| 0x2C11 | Service Cycle Data | org.bluetooth.characteristic.service_cycle_data |
| 0x2C12 | IMD Control | org.bluetooth.characteristic.imd_control |
| 0x2C13 | IMD Historical Data | org.bluetooth.characteristic.imd_historical_data |
| 0x2C14 | RAS Features | org.bluetooth.characteristic.ras_features |
| 0x2C15 | Real-time Ranging Data | org.bluetooth.characteristic.real-time_ranging_data |
| 0x2C16 | On-demand Ranging Data | org.bluetooth.characteristic.on-demand_ranging_data |
| 0x2C17 | RAS Control Point | org.bluetooth.characteristic.ras_control_point |
| 0x2C18 | Ranging Data Ready | org.bluetooth.characteristic.ranging_data_ready |
| 0x2C19 | Ranging Data Overwritten | org.bluetooth.characteristic.ranging_data_overwritten |
| 0x2C1A | Coordinated Set Name | org.bluetooth.characteristic.coordinated_set_name |
| 0x2C1B | Humidity 8 | org.bluetooth.characteristic.humidity_8 |
| 0x2C1C | Illuminance 16 | org.bluetooth.characteristic.illuminance_16 |
| 0x2C1D | Acceleration - 3D | org.bluetooth.characteristic.acceleration_3d |
| 0x2C1E | Precise Acceleration - 3D | org.bluetooth.characteristic.precise_acceleration_3d |
| 0x2C1F | Acceleration Detection Status | org.bluetooth.characteristic.acceleration_detection_status |
| 0x2C20 | Door/Window Status | org.bluetooth.characteristic.door_window_status |
| 0x2C21 | Pushbutton Status 8 | org.bluetooth.characteristic.pushbutton_status_8 |
| 0x2C22 | Contact Status 8 | org.bluetooth.characteristic.contact_status_8 |
| 0x2C23 | HID ISO Properties | org.bluetooth.characteristic.hid_iso_properties |
| 0x2C24 | LE HID Operation Mode | org.bluetooth.characteristic.le_hid_operation_mode |
| 0x2C25 | Cookware Description | org.bluetooth.characteristic.cookware_description |
| 0x2C26 | Recipe Control | org.bluetooth.characteristic.recipe_control |
| 0x2C27 | Recipe Parameters | org.bluetooth.characteristic.recipe_parameters |
| 0x2C28 | Cooking Step Status | org.bluetooth.characteristic.cooking_step_status |
| 0x2C29 | Cooking Zone Capabilities | org.bluetooth.characteristic.cooking_zone_capabilities |
| 0x2C2A | Cooking Zone Desired Cooking Conditions | org.bluetooth.characteristic.cooking_zone_desired_cooking_conditions |
| 0x2C2B | Cooking Zone Actual Cooking Conditions | org.bluetooth.characteristic.cooking_zone_actual_cooking_conditions |
| 0x2C2C | Cookware Sensor Data | org.bluetooth.characteristic.cookware_sensor_data |
| 0x2C2D | Cookware Sensor Aggregate | org.bluetooth.characteristic.cookware_sensor_aggregate |
| 0x2C2E | Cooking Temperature | org.bluetooth.characteristic.cooking_temperature |
| 0x2C2F | Cooking Zone Perceived Power | org.bluetooth.characteristic.cooking_zone_preceived_power |
| 0x2C30 | Kitchen Appliance Airflow | org.bluetooth.characteristic.kitchen_appliance_airflow |
| 0x2C31 | Voice Assistant Name | org.bluetooth.characteristic.voice_assistant_name |
| 0x2C32 | Voice Assistant UUID | org.bluetooth.characteristic.voice_assistant_uuid |
| 0x2C33 | Voice Assistant Service Control Point | org.bluetooth.characteristic.voice_assistant_service_control_point |
| 0x2C34 | Installed Location | org.bluetooth.characteristic.installed_location |
| 0x2C35 | Voice Assistant Session State | org.bluetooth.characteristic.voice_assistant_session_state |
| 0x2C36 | Voice Assistant Session Flag | org.bluetooth.characteristic.voice_assistant_session_flag |
| 0x2C37 | Voice Assistant Supported Languages | org.bluetooth.characteristic.voice_assistant_supported_languages |
| 0x2C38 | Voice Assistant Supported Features | org.bluetooth.characteristic.voice_assistant_supported_features |
| 0x2C39 | HID SCI Mode | org.bluetooth.characteristic.hid_sci_mode |
| 0x2C3A | HID SCI Information | org.bluetooth.characteristic.hid_sci_information |
| 0x2C3B | Tire Pressure | org.bluetooth.characteristic.tire_pressure |
| 0x2C3C | Tire Temperature | org.bluetooth.characteristic.tire_temperature |
| 0x2C3D | Tire Acceleration | org.bluetooth.characteristic.tire_acceleration |
| 0x2C3E | TPMS Properties | org.bluetooth.characteristic.tpms_properties |
| 0x2C3F | TPMS Duty Cycle | org.bluetooth.characteristic.tpms_duty_cycle |
| 0x2C40 | TPMS Position | org.bluetooth.characteristic.tpms_position |
| 0x2C41 | TPMS Signing Key | org.bluetooth.characteristic.tpms_signing_key |

## 描述符（Descriptors，0x2900 起）

| UUID | 名称 | SIG 标识 |
|---|---|---|
| 0x2900 | Characteristic Extended Properties | org.bluetooth.descriptor.gatt.characteristic_extended_properties |
| 0x2901 | Characteristic User Description | org.bluetooth.descriptor.gatt.characteristic_user_description |
| 0x2902 | Client Characteristic Configuration | org.bluetooth.descriptor.gatt.client_characteristic_configuration |
| 0x2903 | Server Characteristic Configuration | org.bluetooth.descriptor.gatt.server_characteristic_configuration |
| 0x2904 | Characteristic Presentation Format | org.bluetooth.descriptor.gatt.characteristic_presentation_format |
| 0x2905 | Characteristic Aggregate Format | org.bluetooth.descriptor.gatt.characteristic_aggregate_format |
| 0x2906 | Valid Range | org.bluetooth.descriptor.valid_range |
| 0x2907 | External Report Reference | org.bluetooth.descriptor.external_report_reference |
| 0x2908 | Report Reference | org.bluetooth.descriptor.report_reference |
| 0x2909 | Number of Digitals | org.bluetooth.descriptor.number_of_digitals |
| 0x290A | Value Trigger Setting | org.bluetooth.descriptor.value_trigger_setting |
| 0x290B | Environmental Sensing Configuration | org.bluetooth.descriptor.es_configuration |
| 0x290C | Environmental Sensing Measurement | org.bluetooth.descriptor.es_measurement |
| 0x290D | Environmental Sensing Trigger Setting | org.bluetooth.descriptor.es_trigger_setting |
| 0x290E | Time Trigger Setting | org.bluetooth.descriptor.time_trigger_setting |
| 0x290F | Complete BR-EDR Transport Block Data | org.bluetooth.descriptor.complete_br_edr_transport_block_data |
| 0x2910 | Observation Schedule | org.bluetooth.descriptor.observation_schedule |
| 0x2911 | Valid Range and Accuracy | org.bluetooth.descriptor.valid_range_accuracy |
| 0x2912 | Measurement Description | org.bluetooth.descriptor.measurement_description |
| 0x2913 | Manufacturer Limits | org.bluetooth.descriptor.manufacturer_limits |
| 0x2914 | Process Tolerances | org.bluetooth.descriptor.process_tolerances |
| 0x2915 | IMD Trigger Setting | org.bluetooth.descriptor.imd_trigger_setting |
| 0x2916 | Cooking Sensor Info | org.bluetooth.descriptor.cooking_sensor_info |
| 0x2917 | Cooking Trigger Setting | org.bluetooth.descriptor.cooking_trigger_setting |

---

## 与本库各篇的关系

- [04-ATT与GATT](04-ATT与GATT.md)：GATT 数据层级（声明/服务/特征/描述符四类 UUID 的角色）
- [07-HOGP-HIDoverGATT](07-HOGP-HIDoverGATT.md)：HID 服务用到的 0x2A4D/0x2A4E/0x2A4F Report 系特征
- [00-索引页](../00-无线概览与USB交汇.md)：本目录导航
