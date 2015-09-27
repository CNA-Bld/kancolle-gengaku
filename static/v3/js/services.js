'use strict';

var kcgengakuServices = angular.module('kcgengakuServices', []);

kcgengakuServices.factory('sharedData', ['$http', function ($http) {
    var ships = [];
    var shipsByType = [];
    var selectedShips = [];
    $http.get('/api?api=ships').then(function (response) {
        var originalShipTypes = response.data.response.filter(function (t) {
            return t.ships.length > 0;
        });
        originalShipTypes.forEach(function (shipType) {
            var thisType = {name: shipType.name, ships: []};
            shipType.ships.forEach(function (ship) {
                var thisShip = {
                    'id': ship['id'],
                    name: ship.name,
                    'type': ship.ctype + '型' + (ship.cid ? ' ' + ship.cid + ' 番艦' : ''),
                    image: '/static/v3/images/avatar/' + ship['id'] + '.png'
                };
                ships.push(thisShip);
                thisType.ships.push(thisShip);
            });
            shipsByType.push(thisType);
        });
    });

    return {
        ships: ships,
        shipsByType: shipsByType,
        selectedShips: selectedShips
    };
}]);
