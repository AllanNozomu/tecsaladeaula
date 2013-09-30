from core.models import Video, Activity, Unit, Lesson, StudentProgress
from rest_framework import serializers


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Video
        fields = ('youtube_id',)


class ActivitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Activity
        fields = ('type','data')


class StudentProgressSerializer(serializers.ModelSerializer):
    complete = serializers.DateTimeField(required=False)

    class Meta:
        model = StudentProgress
        fields = ('unit', 'complete', 'last_access')


class UnitSerializer(serializers.HyperlinkedModelSerializer):
    video = VideoSerializer()
    activity = ActivitySerializer()

    class Meta:
        model = Unit
        fields = ('id', 'video', 'activity', 'position')


class LessonSerializer(serializers.HyperlinkedModelSerializer):
    units = UnitSerializer(many=True)

    class Meta:
        model = Lesson
        fields = ('slug', 'name', 'url', 'units')
