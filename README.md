# OctoPrint Wrapped! 🎁

Get your yearly OctoPrint stats a shareable "wrapped" picture - and let it snow! ❄️

<img src="https://raw.githubusercontent.com/OctoPrint/OctoPrint-Wrapped/main/extras/wrapped-demo.png" width="400" height="400" alt="Demo OctoPrint Wrapped share picture" />

![Demo of snow effect](https://raw.githubusercontent.com/OctoPrint/OctoPrint-Wrapped/main/extras/snowfall-demo.gif)

The stats picture depends on the Achievements plugin being enabled (as it takes care of
the stats collection during the year) and can be opened via the little gift package icon
in the navbar.

The snow effect can always be toggled during the season using the little snowflake icon
in the navbar, and its setting persists through the browser's local storage.

Both wrapped and snowfall are only available from December 1st until January 10th.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/main/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/OctoPrint/OctoPrint-Wrapped/archive/main.zip

## Configuration

The plugin does not have any configuration options.

## Acknowledgements

The snowfall is implemented with a slightly customized version of [pure-snow.js](https://github.com/hyperstown/pure-snow.js),
released under the MIT license and bundled here under `octoprint_wrapped/static/pure-snow`.
