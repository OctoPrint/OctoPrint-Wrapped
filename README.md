# OctoPrint Wrapped! 🎁

Get your yearly OctoPrint stats as a shareable **#OctoPrintWrapped** picture - and let it snow!

<img src="https://raw.githubusercontent.com/OctoPrint/OctoPrint-Wrapped/main/extras/wrapped-demo.png" width="400" height="400" alt="Demo OctoPrint Wrapped share picture" />

![Demo of snow effect](https://raw.githubusercontent.com/OctoPrint/OctoPrint-Wrapped/main/extras/snowfall-demo.gif)

The Wrapped picture depends on the Achievements plugin being enabled (as it takes care of
the stats collection during the year) and can be opened via the little gift package icon 🎁
in the navbar.

The snow effect can always be toggled during the season using the little snowflake icon ❄️
in the navbar, and its setting persists through the browser's local storage.

Both Wrapped and snowfall are only available from December 1st until January 10th.

**If you post your Wrapped on social media, make sure to use the hashtag `#OctoPrintWrapped`! 😊**

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/main/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/OctoPrint/OctoPrint-Wrapped/archive/main.zip

## Configuration

The plugin does not have any configuration options.

## Acknowledgements

The snowfall is implemented with a slightly customized version of [pure-snow.js](https://github.com/hyperstown/pure-snow.js),
released under the MIT license and bundled here under `octoprint_wrapped/static/pure-snow`.

The font used for the stats in the generated wrapped picture is [Open Sans](https://fonts.google.com/specimen/Open+Sans),
released under the SIL Open Font License and bundled here under `octoprint_wrapped/static/fonts`.
