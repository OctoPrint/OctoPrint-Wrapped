import json
import os
from typing import Optional

import flask
import octoprint.plugin
from flask_babel import gettext
from octoprint.access.permissions import Permissions
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


FONT_FILE_OPEN_SANS_BOLD = "open-sans-v15-latin-700.woff"


class YearStats(BaseModel):
    year: int
    prints_completed: int
    total_print_duration: str
    longest_print: str
    busiest_weekday: str
    files_uploaded: int
    octoprint_versions: int


class ApiResponse(BaseModel):
    years: list[int]


class WrappedPlugin(
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.BlueprintPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.TemplatePlugin,
):
    def __init__(self):
        super().__init__()
        self.font_open_sans_bold: str = None

    def initialize(self):
        self._load_font()

    ##~~ AssetPlugin mixin

    def get_assets(self):
        return {
            "clientjs": ["clientjs/wrapped.js"],
            "js": ["js/wrapped.js", "js/ko.src.svgtopng.js"],
        }

    ##~~ BlueprintPlugin mixin

    def is_blueprint_csrf_protected(self):
        return True

    def is_protected(self):
        return True

    @octoprint.plugin.BlueprintPlugin.route("/<int:year>.svg", methods=["GET"])
    def get_svg(self, year):
        if (
            not hasattr(Permissions, "PLUGIN_ACHIEVEMENTS_VIEW")
            or not Permissions.PLUGIN_ACHIEVEMENTS_VIEW.can()
        ):
            flask.abort(403)

        stats = self._get_year_stats(year)
        if stats is None:
            flask.abort(404)

        response = flask.make_response(
            flask.render_template(
                "wrapped.svg.jinja2",
                font_open_sans_bold=self.font_open_sans_bold,
                **stats.model_dump(by_alias=True),
            )
        )
        response.headers["Content-Type"] = "image/svg+xml"
        return response

    ##~~ SimpleApiPlugin mixin

    def is_api_protected(self):
        return True

    def on_api_get(self, request):
        if (
            not hasattr(Permissions, "PLUGIN_ACHIEVEMENTS_VIEW")
            or not Permissions.PLUGIN_ACHIEVEMENTS_VIEW.can()
        ):
            flask.abort(403)

        response = ApiResponse(years=self._get_available_years())
        return flask.jsonify(response.model_dump(by_alias=True))

    ##~~ Softwareupdate hook

    def get_update_information(self):
        return {
            "wrapped": {
                "displayName": "OctoPrint Wrapped!",
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
            {
                "type": "navbar",
                "template": "wrapped_navbar_wrapped.jinja2",
                "custom_bindings": True,
            },
            {
                "type": "navbar",
                "template": "wrapped_navbar_snowfall.jinja2",
                "custom_bindings": True,
            },
        ]

    ##~~ helpers

    def _get_year_stats_folder(self) -> Optional[str]:
        folder = os.path.join(self.get_plugin_data_folder(), "..", "achievements")
        if not os.path.isdir(folder):
            return None
        return folder

    def _get_year_stats_file(self, year: int) -> Optional[str]:
        folder = self._get_year_stats_folder()
        if not folder:
            return None

        year_path = os.path.join(folder, f"{year}.json")
        if not os.path.isfile(year_path):
            return None

        return year_path

    def _get_available_years(self) -> list[int]:
        import re

        stats_folder = self._get_year_stats_folder()
        if not stats_folder:
            return []

        pattern = re.compile(r"\d{4}.json")

        years = []
        for entry in os.scandir(stats_folder):
            if not entry.is_file():
                continue

            if pattern.fullmatch(entry.name):
                year, _ = os.path.splitext(entry.name)
                years.append(int(year))

        return years

    def _get_year_stats(self, year: int) -> Optional[YearStats]:
        stats_file = self._get_year_stats_file(year)
        if not stats_file:
            return None

        try:
            with open(stats_file) as f:
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

        if days >= 100:
            # strip the minutes to keep things fitting...
            return f"{days}d {hours}h"
        else:
            return f"{days}d {hours}h {minutes}m"

    def _to_duration_hours(self, seconds: int) -> str:
        hours = int(seconds / SECONDS_HOUR)
        seconds -= hours * SECONDS_HOUR

        minutes = int(seconds / SECONDS_MINUTE)
        seconds -= minutes * SECONDS_MINUTE

        return f"{hours}h {minutes}m"

    def _load_font(self) -> None:
        from base64 import b64encode

        font_path = os.path.join(
            os.path.dirname(__file__), "static", "fonts", FONT_FILE_OPEN_SANS_BOLD
        )

        try:
            with open(font_path, "rb") as f:
                data = f.read()

            encoded = b64encode(data).decode().strip()
            self.font_open_sans_bold = f"data:font/woff;base64,{encoded}"
        except Exception:
            self._logger.exception("Error creating data URI for embedded font")


__plugin_name__ = "OctoPrint Wrapped!"
__plugin_pythoncompat__ = ">=3.9,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = WrappedPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
    }
