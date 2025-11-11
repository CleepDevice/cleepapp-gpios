/**
 * Gpios service
 * Handle gpios module requests
 */
angular
.module('Cleep')
.service('gpiosService', ['$q', '$rootScope', 'rpcService', 'cleepService',
function($q, $rootScope, rpcService, cleepService) {
    var self = this;
    
    /**
     * Init module devices
     */
    self.initDevices = function(devices) {
        for( var uuid in devices ) {
            // change current color if gpio is on
            if( devices[uuid].on ) {
                devices[uuid].__widget.mdcolors = '{background:"default-accent-400"}';
            }
        }

        return devices;
    };

    /**
     * Return raspi gpios (according to board version)
     */
    self.getRaspiGpios = function() {
        return rpcService.sendCommand('get_raspi_gpios', 'gpios');
    };

    /**
     * Return list of assigned gpios
     */
    self.getAssignedGpios = function() {
        return rpcService.sendCommand('get_assigned_gpios', 'gpios');
    };

    /**
     * Return gpios usage
     */
    self.getPinsUsage = function() {
        return rpcService.sendCommand('get_pins_usage', 'gpios');
    };

    /**
     * Add new gpio
     */
    self.addGpio = function(name, gpio, mode, keep, inverted) {
        return rpcService.sendCommand('add_gpio', 'gpios', {'name':name, 'gpio':gpio, 'mode':mode, 'keep':keep, 'inverted':inverted})
            .then(function(resp) {
                return $q.all(cleepService.reloadModuleConfig('gpios'), cleepService.reloadDevices());
            })
    };

    /**
     * Delete gpio
     */
    self.deleteGpio = function(uuid) {
        return rpcService.sendCommand('delete_gpio', 'gpios', {'device_uuid':uuid})
            .then(function(resp) {
                return $q.all(cleepService.reloadModuleConfig('gpios'), cleepService.reloadDevices());
            });
    };

    /**
     * Update device
     */
    self.updateGpio = function(uuid, name, keep, inverted) {
        return rpcService.sendCommand('update_gpio', 'gpios', {'device_uuid':uuid, 'name':name, 'keep':keep, 'inverted':inverted})
            .then(function(resp) {
                return $q.all(cleepService.reloadModuleConfig('gpios'), cleepService.reloadDevices());
            });
    };

    /**
     * Turn on specified gpio
     */
    self.turnOn = function(uuid) {
        return rpcService.sendCommand('turn_on', 'gpios', {'device_uuid':uuid});
    };

    /**
     * Turn off specified gpio
     */
    self.turnOff = function(uuid) {
        return rpcService.sendCommand('turn_off', 'gpios', {'device_uuid':uuid});
    };
}]);

