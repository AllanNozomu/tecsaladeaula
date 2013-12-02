
(function (angular) {
    'use strict';
    /* Controllers */
    angular.module('notes.controllers', []).
        controller('NoteCtrl', ['$scope', '$window', 'LessonData', 'Note',
            function ($scope, $window, LessonData, Note) {
                $scope.save_note = function() {
                    $scope.note.text = $scope.note_text;
                    if ($scope.note.id) {
                        $scope.note.$update({note_id: $scope.note.id});
                    } else {
                        $scope.note.$save();
                    }
                };

                LessonData.then(function (lesson) {
                    var currentUnit = lesson.units[$scope.currentUnitPos - 1];
                    var currentUnitId = currentUnit.id;
                    Note.get({content_type: window.unit_content_type_id, object_id: currentUnitId}, function (notes) {
                        if (notes.length > 0){
                            $scope.note = notes[0];
                        } else {
                            $scope.note = new Note();
                            $scope.note.content_type = window.unit_content_type_id;
                            $scope.note.object_id = currentUnitId;
                        }
                        $scope.note_text = $scope.note.text;
                    });
                });
    }]);
})(angular);
