# `hass-free-sleep`

An unofficial Home Assistant custom integration for Free Sleep devices.

> [!NOTE]
> This integration was only tested with an Eight Sleep Pod 4, and does not
> guarantee compatibility with other Eight Sleep devices. Some functionality
> like the Pod 5 base adjustments are not supported at this time.
> 
> Some functionality like vitals may not be accurate.

This integration allows you to control and monitor your Free Sleep device
directly from Home Assistant. You can adjust bed settings, monitor sleep data,
and view historical sleep information.

It creates three devices in Home Assistant:

- A device representing the pod itself, allowing control over the pod.
- Two devices representing each side of the bed, providing access to
  side-specific settings and data, such as temperature and sleep metrics.

## Features

- Control bed settings such as temperature and alarms.
- Monitor sleep data including heart rate, respiratory rate, and HRV.
- View historical sleep data through Home Assistant's UI.
- Enable or disable features like daily priming and away mode.

## Installation

### Installation via HACS (Recommended)

Installation can be done via HACS (Home Assistant Community Store), by following
these steps.

#### 1. Add repository to HACS

1. Navigate to the HACS section in Home Assistant.
2. Click on the three dots in the top right corner and select "Custom
   repositories".
3. Enter the repository URL: `https://github.com/Mrtenz/hass-free-sleep` and
   select "Integration" as the category.
4. Click "Add".

#### 2. Install the integration

1. Navigate to the HACS section in Home Assistant.
2. Search for "Free Sleep" and click on it.
3. Click "Download" to install the integration.
4. Restart Home Assistant.

### Manual Installation

1. Copy the contents of the `custom_components/free_sleep` directory from the
   repository to your Home Assistant's `custom_components/free_sleep` directory.
2. Restart Home Assistant.

## Configuration

After installation, you can configure the integration through the Home Assistant
UI:

1. Navigate to "Settings" > "Devices & Services".
2. Click on "Add Integration" and search for "Free Sleep".
3. Follow the prompt to enter the hostname or IP address of your Free Sleep
   device.
