(function(angular){
    'use strict';

    var app = angular.module('new-course', ['ngResource', 'directive.markdowneditor']);

    app.config(['$httpProvider',
        function ($httpProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        }
    ]);
})(window.angular);