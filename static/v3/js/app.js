'use strict';

var kcgengakuApp = angular.module('kcgengakuApp', [
    'ngRoute',
    'ngMaterial',
    'kcgengakuControllers',
    'kcgengakuServices'
]);

kcgengakuApp.config(['$routeProvider',
    function ($routeProvider) {
        $routeProvider.
            when('/ships', {
                templateUrl: '/static/v3/ships.html',
                controller: 'ShipListCtrl'
            }).
            when('/result', {
                templateUrl: '/static/v3/result.html',
                controller: 'ResultCtrl'
            }).
            when('/recipe/:constructType/:recipe', {
                templateUrl: '/static/v3/recipe.html',
                controller: 'RecipeCtrl'
            }).
            when('/gengaku3', {
                templateUrl: '/static/v3/tanaka.html'
            }).
            when('/tanaka', {
                templateUrl: '/static/v3/tanaka.html'
            }).
            otherwise({
                redirectTo: '/ships'
            });
    }]);
