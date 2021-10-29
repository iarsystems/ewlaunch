# EWlaunch

__EWlaunch__ lets you select the version of _IAR Embedded Workbench_ to use with any given workspace:

![ewlaunch-demo](ewlaunch.png)

This is useful when you have multiple versions of _IAR Embedded Workbench_ installed, to work around the operating system's file extension association limitation. Once a version is selected, the choice can be stored in a corresponding `<workspace>.custom_argvars` file. When this option is used, the next time the workspace is launched, it will use the previously selected version.

Existing _IAR Embedded Workbench_ installations are automatically located from the _Windows Registry_. You can also manually specify installation directories.

If you end up with a question or suggestion specifically related to the [__EWlaunch utility__][url-repo-home], you might be interested in verifying if it was already discussed in [earlier issues][url-repo-issue-old]. If you could not find what you are looking for, feel free to [create a new issue][url-repo-issue-new].

It is possible to receive [notifications][url-gh-docs-notify] about updates in your GitHub inbox by starting to __watch__ this repository.

## Setup

Edit the file `context_menu.reg` with the path to `ewlaunch.exe`, and run it to add the entries to the registry. This makes __EWlaunch__ available as a context menu action, accessible by right-clicking on a file/folder in the Windows file explorer.

Optionally, see [ewlaunch.ini](ewlaunch.ini) for configuration options, and [installations.ini](installations.ini) to manually specify installation locations.


## Usage

Below are some examples of how to perform common tasks using __EWlaunch__:

### Open an existing workspace (.eww) file
Right-click on a `<workspace>.eww` file, or on a folder containing a `<workspace>.eww` file. Select __EWlaunch__ in the context menu.

__EWlaunch__ inspects the corresponding `.custom_argvars` file to discover which version of _IAR Embedded Workbench_ to launch. If it does not find such information, then a selection dialog will be shown.

To always show the selection dialog, even when the version is already known, start __EWlaunch__ by right-clicking on the `<workspace>.custom_argvars` file instead.

### Create a new workspace
Right-click on a folder (that does not contain a `.eww` file) and select __EWlaunch__, to create a new empty workspace for the selected version of _IAR Embedded Workbench_. The new workspace is automatically launched in the selected version of the IDE.

### Launch without workspace
When an empty workspace name is used, __EWlaunch__ launches the selected version of the _IAR Embedded Workbench_ with no opened workspace.


## Version history
- 1.0 - 2020-11-01 - Initial version

<!-- Links -->
[url-repo-home]:         https://github.com/IARSystems/ewlaunch
[url-repo-issue-new]:    https://github.com/IARSystems/ewlaunch/issues/new
[url-repo-issue-old]:    https://github.com/IARSystems/ewlaunch/issues?q=is%3Aissue+is%3Aopen%7Cclosed
[url-gh-docs-notify]:    https://docs.github.com/en/github/managing-subscriptions-and-notifications-on-github/setting-up-notifications/about-notifications
