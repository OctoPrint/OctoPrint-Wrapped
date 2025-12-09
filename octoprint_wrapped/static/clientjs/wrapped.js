(function (global, factory) {
    if (typeof define === "function" && define.amd) {
        define(["OctoPrintClient"], factory);
    } else {
        factory(global.OctoPrintClient);
    }
})(this, function (OctoPrintClient) {
    var OctoPrintWrappedClient = function (base) {
        this.base = base;

        this.baseUrl = this.base.getBlueprintUrl("wrapped");
        this.apiUrl = this.base.getSimpleApiUrl("wrapped");
    };

    OctoPrintWrappedClient.prototype.get = function (opts) {
        return this.base.get(this.apiUrl, opts);
    };

    OctoPrintWrappedClient.prototype.getYearSvgUrl = function (year, opts) {
        return this.baseUrl + year + ".svg";
    };

    // register plugin component
    OctoPrintClient.registerPluginComponent("wrapped", OctoPrintWrappedClient);

    return OctoPrintWrappedClient;
});
