'use strict';

var kcgengakuControllers = angular.module('kcgengakuControllers', []);

kcgengakuControllers.controller('MainCtrl', ['$scope', '$http', '$location', '$window', '$mdSidenav',
    function ($scope, $http, $location, $window, $mdSidenav) {
        $scope.toggleSidenav = function () {
            $mdSidenav('left').toggle();
        };
        $scope.sidenavItems = [{
            'title': '建造统计',
            'view': 'ships'
        }, {
            'title': '一式玄学弹（未实装）',
            'view': 'gengaku3'
        }, {
            'title': '田中灵车漂移装置',
            'view': 'tanaka'
        }];
        $scope.sidenavItemClick = function (item) {
            $location.path(item['view']);
        };
        $scope.hitokoto = undefined;
        $http.jsonp('http://api.hitokoto.us/rand?encode=jsc&fun=JSON_CALLBACK').then(function (response) {
            var d = response.data;
            $scope.hitokoto = {
                'link': 'http://hitokoto.us/view/' + d.id + '.html',
                'hover': '分类：' + d.catname + '\n出自：' + d.source + '\n喜欢：' + d.like + '\n投稿：' + d.author + ' @ ' + d.date,
                'hitokoto': d.hitokoto
            };
        });
        $scope.openHitokoto = function() {
            $window.open($scope.hitokoto['link']);
        };
    }]).controller('ShipListCtrl', ['$scope', '$location', 'sharedData',
    function ($scope, $location, sharedData) {
        $scope.selectedShips = sharedData.selectedShips;
        $scope.ships = sharedData.ships;
        $scope.shipsByType = sharedData.shipsByType;
        $scope.toggleSelected = function (ship) {
            var index = $scope.selectedShips.indexOf(ship);
            if (index < 0) {
                $scope.selectedShips.push(ship);
            } else {
                $scope.selectedShips.splice(index, 1);
            }
        };
        function createFilterFor(query) {
            var lowercaseQuery = angular.lowercase(query);
            return function filterFn(ship) {
                return (ship.name.toLowerCase().indexOf(lowercaseQuery) != -1);
            };
        }

        $scope.querySearch = function (query) {
            var results = query ?
                $scope.ships.filter(createFilterFor(query)) : [];
            return results;
        };

        $scope.changeView = function (view) {
            $location.path(view);
        }

    }]).controller('ResultCtrl', ['$scope', '$http', '$location', 'sharedData',
    function ($scope, $http, $location, sharedData) {
        $scope.selectedShips = sharedData.selectedShips;
        if ($scope.selectedShips.length == 0) {
            $location.path('ships');
        } else {
            $scope.constructData = undefined;

            var shipsToQuery = $scope.selectedShips.map(function (e) {
                return e['id'];
            });

            $http.get('/api?api=construct&ships=' + JSON.stringify(shipsToQuery)).then(function (response) {
                $scope.constructData = response.data.response;
                $scope.constructData['general'].forEach(parseRecipe);
                $scope.constructData['general'].sort(compareProb);
                $scope.constructData['large'].forEach(parseRecipe);
                $scope.constructData['large'].sort(compareProb);
            });
        }

        $scope.recipeClick = function (constructType, recipe) {
            $location.path('recipe/' + constructType + '/' + JSON.stringify(recipe));
        };

        function parseRecipe(recipe) {
            recipe['succ_sum'] = 0;
            shipsToQuery.forEach(function (ship) {
                recipe['succ_sum'] += recipe['succ_individual'][ship] || 0;
            });
            recipe['prob'] = 100.0 * recipe['succ_sum'] / recipe['sum'];
        }

        function compareProb(a, b) {
            return b['prob'] - a['prob'];
        }
    }]).controller('RecipeCtrl', ['$scope', '$http', '$location', '$routeParams', 'sharedData',
    function ($scope, $http, $location, $routeParams, sharedData) {
        $scope.recipe = JSON.parse($routeParams.recipe).join('/');
        $scope.getShipById = function (shipId) {
            return sharedData.ships.filter(function (t) {
                return t['id'] == shipId;
            })[0];
        };
        $http.get('/api?api=recipe&type=' + $routeParams.constructType + '&recipe=' + $routeParams.recipe).then(function (response) {
            $scope.recipeData = response.data.response;
        });
    }]);
