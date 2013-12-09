(function(angular){
    'use strict';
    var app = angular.module('new-course');

    app.factory('Course', ['$resource', function($resource) {
        var Course = $resource('/api/course/:slug', {'slug':'@slug'});
        return Course;
    }]);

    app.factory('VideoData', ['$document', '$q', function($document, $q){
        var funcName = 'getYoutubeData'+Math.random().toString(16).substring(2);
        var feed = {};

        var VideoData = function() {
            this.getData = function(){
                return feed.data;
            };

            this.load = function(vid) {
                this.deferred = $q.defer();

                this.src = 'http://gdata.youtube.com/feeds/api/videos/'+
                            vid + '?alt=json&callback=' + funcName;

                var script = $document[0].createElement('script');
                script.type = 'text/javascript';
                script.src = this.src;
                $document[0].body.appendChild(script);

                return this.deferred.promise;
            };
        };
        var vd = new VideoData();

        window[funcName] = function(data) {
            feed.data = data;
            vd.deferred.resolve(data);
            return feed;
        };

        return vd;
    }]);
})(window.angular);