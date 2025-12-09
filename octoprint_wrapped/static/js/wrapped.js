/*
 * View model for OctoPrint-Wrapped
 *
 * Author: Gina Häußge
 * License: AGPL-3.0-or-later
 */
$(function () {
    const FLAKES = 50;

    const MONTH_DECEMBER = 11;
    const MONTH_JANUARY = 0;

    const SNOWFALL_LOCAL_STORAGE_KEY = "plugin.wrapped.snowfall";
    const snowfallToLocalStorage = (value) => {
        saveToLocalStorage(SNOWFALL_LOCAL_STORAGE_KEY, {
            enabled: value
        });
    };

    const snowfallFromLocalStorage = () => {
        const data = loadFromLocalStorage(SNOWFALL_LOCAL_STORAGE_KEY);
        if (data["enabled"] !== undefined) return !!data["enabled"];
        return false;
    };

    function WrappedViewModel(parameters) {
        const self = this;

        self.loginState = parameters[0];
        self.access = parameters[1];
        self.aboutVM = parameters[2];

        self.availableYears = ko.observableArray([]);

        self.snowfallEnabled = false;
        self.snowfallContainer = undefined;

        self.currentWrapped = ko.pureComputed(() => {
            if (!self.withinWrappedSeason()) return false;

            const now = new Date();
            const year =
                now.getMonth() == MONTH_DECEMBER
                    ? now.getFullYear() // still in December
                    : now.getFullYear() - 1; // already January
            const years = self.availableYears();

            if (years.indexOf(year) !== -1 && self.withinWrappedSeason()) {
                return year;
            } else {
                return false;
            }
        });

        self.currentWrappedAvailable = ko.pureComputed(() => {
            return self.currentWrapped() !== false;
        });

        self.currentSvgUrl = ko.pureComputed(() => {
            const year = self.currentWrapped();
            if (!year) return false;

            return OctoPrint.plugins.wrapped.getYearSvgUrl(year);
        });

        self.withinWrappedSeason = ko.pureComputed(() => {
            // wrapped Season = Dec 1st until January 10th
            const now = new Date();
            return (
                now.getMonth() == MONTH_DECEMBER ||
                (now.getMonth() == MONTH_JANUARY && now.getDate() < 10)
            );
        });

        self.requestData = () => {
            if (
                !self.loginState.hasPermission(
                    self.access.permissions.PLUGIN_ACHIEVEMENTS_VIEW
                )
            ) {
                return;
            }
            OctoPrint.plugins.wrapped.get().done(self.fromResponse);
        };

        self.fromResponse = (response) => {
            self.availableYears(response.years);
        };

        self.showWrapped = () => {
            self.aboutVM.show("about_plugin_wrapped");
            return false;
        };

        self.toggleSnowfall = () => {
            self.snowfallEnabled = !self.snowfallEnabled;
            snowfallToLocalStorage(self.snowfallEnabled);
            self.updateSnowfall();
        };

        self.updateSnowfall = () => {
            let container = document.getElementById("snow");

            const body = document.getElementsByTagName("body")[0];
            const head = document.getElementsByTagName("head")[0];

            if (!self.snowfallEnabled) {
                if (showSnow !== undefined) showSnow(false);
            } else if (self.snowfallEnabled) {
                if (!self.withinWrappedSeason()) return;

                if (!container) {
                    container = document.createElement("div");
                    container.id = "snow";
                    container.dataset.count = FLAKES;
                    body.insertBefore(container, body.firstChild);

                    const styleSnow = document.createElement("link");
                    styleSnow.href =
                        BASEURL + "plugin/wrapped/static/pure-snow/pure-snow.css";
                    styleSnow.rel = "stylesheet";
                    head.appendChild(styleSnow);

                    const scriptSnow = document.createElement("script");
                    scriptSnow.src =
                        BASEURL + "plugin/wrapped/static/pure-snow/pure-snow.js";
                    scriptSnow.defer = true;
                    scriptSnow.onload = () => {
                        setTimeout(() => {
                            createSnow();
                            showSnow(true);
                        }, 500);
                    };
                    head.appendChild(scriptSnow);
                } else {
                    if (showSnow !== undefined) showSnow(true);
                }
            }
        };

        self.onUserPermissionsChanged =
            self.onUserLoggedIn =
            self.onUserLoggedOut =
                (user) => {
                    if (
                        self.loginState.hasPermission(
                            self.access.permissions.PLUGIN_ACHIEVEMENTS_VIEW
                        )
                    ) {
                        self.requestData();
                    }
                };

        self.onStartup = () => {
            self.snowfallEnabled = snowfallFromLocalStorage();
            self.updateSnowfall();
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: WrappedViewModel,
        dependencies: ["loginStateViewModel", "accessViewModel", "aboutViewModel"],
        elements: [
            "#about_plugin_wrapped",
            "#navbar_plugin_wrapped",
            "#navbar_plugin_wrapped_2"
        ]
    });
});
