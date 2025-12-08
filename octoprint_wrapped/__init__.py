import json
import os
from typing import Optional

import flask
import octoprint.plugin
from flask_babel import gettext
from octoprint.schema import BaseModel

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
SECONDS_MINUTE = 60
SECONDS_HOUR = SECONDS_MINUTE * 60
SECONDS_DAY = SECONDS_HOUR * 24


class YearStats(BaseModel):
    year: int
    prints_completed: int
    total_print_duration: str
    longest_print: str
    busiest_weekday: str
    files_uploaded: int
    octoprint_versions: int


class WrappedPlugin(
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.BlueprintPlugin,
    octoprint.plugin.TemplatePlugin,
):
    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/wrapped.js"],
            "css": ["css/wrapped.css"],
            "less": ["less/wrapped.less"],
        }

    ##~~ BlueprintPlugin mixin

    def is_blueprint_csrf_protected(self):
        return True

    def is_protected(self):
        return True

    @octoprint.plugin.BlueprintPlugin.route("/<int:year>.svg", methods=["GET"])
    def get_svg(self, year):
        stats = self._get_year_stats(year)
        if stats is None:
            flask.abort(404)

        response = flask.make_response(
            flask.render_template(
                "wrapped.svg.jinja2", **stats.model_dump(by_alias=True)
            )
        )
        response.headers["Content-Type"] = "image/svg+xml"
        return response

    ##~~ Softwareupdate hook

    def get_update_information(self):
        return {
            "wrapped": {
                "displayName": "Wrapped Plugin",
                "displayVersion": self._plugin_version,
                # version check: github repository
                "type": "github_release",
                "user": "OctoPrint",
                "repo": "OctoPrint-Wrapped",
                "current": self._plugin_version,
                # update method: pip
                "pip": "https://github.com/OctoPrint/OctoPrint-Wrapped/archive/{target_version}.zip",
            }
        }

    ##~~ TemplatePlugin mixin

    def is_template_autoescaped(self):
        return True

    def get_template_configs(self):
        return [
            {
                "type": "about",
                "name": gettext("OctoPrint Wrapped!"),
                "template": "wrapped_about.jinja2",
                "custom_bindings": True,
            },
        ]

    ##~~ helpers

    def _get_year_stats(self, year: int) -> Optional[YearStats]:
        achievements_data_folder = os.path.join(
            self.get_plugin_data_folder(), "..", "achievements"
        )
        if not os.path.exists(achievements_data_folder):
            return None

        stats_file = os.path.join(achievements_data_folder, f"{year}.json")
        if not os.path.exists(stats_file):
            return None

        try:
            with open(stats_file, "r") as f:
                stats = json.load(f)
        except Exception:
            self._logger.exception(
                f"Error while reading yearly stats for {year} from {stats_file}"
            )
            return None

        try:
            weekday_stats = stats.get("prints_started_per_weekday", {})
            busiest = None
            for key, value in weekday_stats.items():
                if busiest is None or value > busiest[1]:
                    busiest = (key, value)

            if busiest:
                weekday = WEEKDAYS[int(busiest[0])]
            else:
                weekday = "-"

            return YearStats(
                year=year,
                prints_completed=stats.get("prints_finished", 0),
                total_print_duration=self._to_duration_days(
                    int(stats.get("print_duration_total", 0))
                ),
                longest_print=self._to_duration_hours(
                    int(stats.get("longest_print_duration", 0))
                ),
                busiest_weekday=weekday,
                files_uploaded=int(stats.get("files_uploaded", 0)),
                octoprint_versions=int(stats.get("seen_versions", 1)),
            )
        except Exception:
            self._logger.exception(
                f"Error while parsing yearly stats for {year} from {stats_file}"
            )
            return None

    def _to_duration_days(self, seconds: int) -> str:
        days = int(seconds / SECONDS_DAY)
        seconds -= days * SECONDS_DAY

        hours = int(seconds / SECONDS_HOUR)
        seconds -= hours * SECONDS_HOUR

        minutes = int(seconds / SECONDS_MINUTE)
        seconds -= minutes * SECONDS_MINUTE

        if seconds >= 30:
            minutes += 1

        return f"{days}d {hours}h {minutes}m"

    def _to_duration_hours(self, seconds: int) -> str:
        hours = int(seconds / SECONDS_HOUR)
        seconds -= hours * SECONDS_HOUR

        minutes = int(seconds / SECONDS_MINUTE)
        seconds -= minutes * SECONDS_MINUTE

        if seconds >= 30:
            minutes += 1

        return f"{hours}h {minutes}m"


__plugin_name__ = "OctoPrint Wrapped!"
__plugin_pythoncompat__ = ">=3.7,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = WrappedPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
