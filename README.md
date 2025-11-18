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

#### Add repository to HACS

Installation can be done via HACS (Home Assistant Community Store), by clicking
on the button below:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Mrtenz&repository=hass-free-sleep)

Alternatively, you can manually install the integration by following these
steps:

1. Navigate to the HACS section in Home Assistant.
2. Click on the three dots in the top right corner and select "Custom
   repositories".
3. Enter the repository URL: `https://github.com/Mrtenz/hass-free-sleep` and
   select "Integration" as the category.
4. Click "Add".

#### Install the integration

1. Go to HACS in Home Assistant.
2. Click on "Integrations".
3. Search for "Free Sleep" and click on it.
4. Click "Download" to install the integration.
5. Restart Home Assistant.

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
