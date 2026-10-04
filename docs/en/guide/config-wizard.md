# F2 Configuration Wizard Guide

## Introduction

The F2 Configuration Wizard is an interactive tool that helps users quickly generate F2 configuration files. It provides a scaffolding experience similar to `pnpm create`, `npm init`, or `vue create`, making configuration simple and intuitive.

## Features

- 🎯 **Interactive Configuration**: Guide users through configuration with simple Q&A
- 🔧 **Smart Prompts**: Provide detailed field descriptions and examples
- 📱 **Multi-platform Support**: Support for DouYin, TikTok, Weibo, Twitter, and more
- 🎨 **Beautiful Interface**: Colorful, formatted terminal interface using Rich library
- ✅ **Configuration Validation**: Preview and confirm configuration before saving
- 📁 **Flexible Output**: Support custom configuration file save paths
- 🎛️ **Advanced Options**: Support for naming templates, date intervals, download limits, and more
- 💬 **Comment Preservation**: Use ruamel.yaml to preserve comments and formatting in config files
- 🔄 **Smart Defaults**: Provide reasonable default configuration options for different platforms

## Usage

### Basic Usage

```bash
# Start configuration wizard
f2 config-wizard
```

### Specify Output File

```bash
# Specify the configuration file save path; the wizard no longer asks for it
f2 config-wizard -o my_custom_config.yaml
```

### Specify Application

```bash
# Configure only the given application (douyin, tiktok, weibo or twitter) and skip choosing platforms
f2 config-wizard -a douyin
```

## Configuration Process

### 1. Welcome Screen

The configuration wizard displays welcome information and feature introduction when started.

### 2. Platform Selection

Select applications to configure from the supported platform list:

- DouYin (抖音)
- TikTok
- Weibo (微博)
- Twitter (X)

You can select multiple platforms, separated by commas, e.g., `1,2`

### 3. Parameter Configuration

For each selected platform, the wizard will guide you to configure:

#### Required Parameters
- **URL**: Target link
- **Mode**: Download mode (user posts, liked posts, live streams, etc.)
- **Cookie**: Authentication information (can choose to configure later)

#### Optional Parameters
- **Save Path**: Download file save location
- **File Naming**: Custom file naming template
- **Folder Organization**: Whether to create subfolders by user
- **Network Settings**: Timeout, retry count, etc.
- **Download Limits**: Maximum download count control
- **Date Filtering**: Filter content by date interval

### 4. Preview and Confirmation

After configuration is complete, the wizard displays a complete configuration preview. You can:
- Confirm configuration and save
- Cancel and reconfigure
- Modify save path

### 5. Save Configuration

After confirmation, the configuration file will be saved to the specified location, and the wizard will show usage instructions.

## Configuration Examples

### DouYin Configuration Example

```yaml
douyin:
  url: https://v.douyin.com/your-url-here
  mode: post
  path: Download/DouYin
  naming: "{create}_{desc}"
  folderize: true
  timeout: 10
  max_retries: 3
  max_counts: 100
  interval: "2025-01-01|2025-12-31"
```

### Multi-platform Configuration Example

```yaml
douyin:
  url: https://v.douyin.com/your-douyin-url
  mode: post
  path: Download/DouYin
  naming: "{create}_{desc}"
  interval: "all"

tiktok:
  url: https://www.tiktok.com/@username
  mode: like
  path: Download/TikTok
  naming: "{create_time}_{author}"
  max_counts: 50
```

## Using Generated Configuration

After the configuration file is generated, you can use it like this:

```bash
# Use configuration file
f2 dy -c your_config.yaml

# Or for multi-platform configuration
f2 dy -c multi_platform_config.yaml
f2 tk -c multi_platform_config.yaml
```

## Advanced Features

### Field Type Description

- **str**: String type, such as URL, path, etc.
- **int**: Integer type, such as timeout, retry count, etc.
- **bool**: Boolean type, such as whether to create folders, etc.
- **choice**: Choice type, such as download mode, naming template, etc.

### Advanced Configuration Options

#### Naming Templates
The configuration wizard supports multiple naming template options:
- `{create}_{desc}`: Creation time_Content description
- `{nickname}_{create}_{desc}`: User nickname_Creation time_Content description
- `{aweme_id}_{desc}`: Content ID_Content description
- Custom template: Support user-defined naming rules

#### Date Interval Filtering
Support multiple date filtering methods:
- `all`: Download all content (default)
- `2025-01-01|2025-12-31`: Specify year range
- `recent_month`: Last month
- `recent_week`: Last week
- Custom interval: User-specified date range

#### Download Count Control
You can set maximum download count:
- `0`: No limit (default)
- `10`, `50`, `100`, `500`: Common count options
- Custom count: User-specified specific count

### Default Value Handling

The configuration wizard automatically reads F2's default configuration template to provide appropriate default values for each field.

### Input Validation and Error Handling

- **Input Validation**: Ensure input values meet field requirements
- **Empty Value Handling**: Provide reasonable defaults or prompt for re-input for empty inputs
- **File Permission Check**: Ensure write permission to specified path
- **Configuration Integrity Validation**: Ensure all required fields are configured
- **Interrupt Handling**: Support Ctrl+C for safe exit from configuration process

## Relationship with Existing Configuration System

Configuration files generated by the wizard are fully compatible with F2's existing configuration system:

- Support high/low frequency parameter separation
- Compatible with `--init-config` and `--update-config` commands
- Can be mixed with manually edited configuration files
- Follow existing configuration file format and conventions
- Use ruamel.yaml to preserve comments and formatting
- Support incremental updates to configuration files

## Troubleshooting

### Common Issues

1. **Command not found**
   ```bash
   # Make sure to use the correct command
   f2 config-wizard
   # Not f2 config wizard
   ```

2. **Permission error**
   ```bash
   # Make sure you have write permission to the output directory
   f2 config-wizard -o ~/my_configs/f2.yaml
   ```

3. **Invalid configuration file**
   - Check if YAML format is correct
   - Ensure all required fields are filled

4. **Interrupt handling error**
   - Use Ctrl+C to safely exit the configuration process
   - If you encounter abnormal interruption, restart the wizard

5. **Empty input handling**
   - Most fields support empty input using default values
   - For required fields, you will be prompted to re-enter

### Getting Help

```bash
# View configuration wizard help
f2 config-wizard --help

# View F2 overall help
f2 --help
```

## Developer Notes

### Extending Application Support

To add new application support, you need to add corresponding configuration to the `app_info` dictionary in the `ConfigWizard` class.

### Custom Fields

New configuration fields can be defined in the `field_descriptions` dictionary, including type, description, default value, etc.

### Localization Support

The configuration wizard supports internationalization, all user-visible strings are wrapped with `_()` function for easy translation.

## Feedback and Contribution

If you encounter problems or have suggestions for improvement when using the configuration wizard, welcome to:

1. Submit Issues to the GitHub repository
2. Contribute code to improve functionality
3. Provide documentation translations

The configuration wizard makes F2 more user-friendly, and we hope it brings you a great experience!
