(function(angular){

    var app = angular.module('new-course');

    app.controller('CourseEditController', ['$scope', 'Course', '$filter', 'youtubePlayerApi', 'VideoData',
        function($scope, Course, $filter, youtubePlayerApi, VideoData) {
            $scope.course = new Course({'status':'new','intro_video': {'youtube_id':''}});
            $scope.errors = {};

            var player;
            youtubePlayerApi.$watch('playerId', function(){
                youtubePlayerApi.videoId = $scope.course.intro_video.youtube_id;
                youtubePlayerApi.playerWidth = '100%';
                youtubePlayerApi.playerHeight = '475px';
                youtubePlayerApi.loadPlayer().then(function(p){
                    player = p;
                });
                window.p = player;
            });

            $scope.$watch('course.intro_video.youtube_id', function(vid){
                if(!vid) return;
                player && player.cueVideoById(vid);
                VideoData.load(vid).then(function(data){
                    $scope.course.intro_video.name = data.entry.title.$t;
                });
            });

            $scope.saveCourse = function() {
                if(!$scope.course.slug)
                    $scope.course.slug = $filter('slugify')($scope.course.name);

                $scope.course.$save().catch(function(response){
                    $scope.errors = response.data;
                });
            };
        }
    ]);

})(window.angular);