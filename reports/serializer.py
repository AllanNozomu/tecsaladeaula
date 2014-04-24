# -*- coding: utf-8 -*-
from rest_framework import serializers
from core.models import CourseStudent, Course


# class LessonUserStatsSerializer(serializers.ModelSerializer):
#
#     forum_questions = serializers.SerializerMethodField('get_full_name')
#     forum_answers = serializers.SerializerMethodField('get_full_name')
#     notes = serializers.SerializerMethodField('get_full_name')
#     progress = serializers.SerializerMethodField('get_full_name')
#
#     class Meta:
#         model = Lesson
#         fields = ('',)


class UserCourseStats(serializers.ModelSerializer):

    name = serializers.SerializerMethodField('get_full_name')
    username = serializers.SerializerMethodField('get_username')
    email = serializers.SerializerMethodField('get_email')
    course_progress = serializers.SerializerMethodField('get_user_progress')
    lessons_progress = serializers.SerializerMethodField('get_lesson_progress')
    forum_questions = serializers.SerializerMethodField('get_forum_questions')
    forum_answers = serializers.SerializerMethodField('get_forum_answers')
#     lessons_stats = LessonUserStatsSerializer(many=True, allow_add_remove=False)

    class Meta:
        model = CourseStudent
        fields = ('name', 'username', 'email', 'course_progress', 'lessons_progress', 'forum_questions', 'forum_answers')

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    def get_user_progress(self, obj):
        return obj.percent_progress()

    def get_lesson_progress(self, obj):
        return obj.percent_progress_by_lesson()

    def get_forum_questions(self, obj):
        return obj.forum_questions_by_lesson()

    def get_forum_answers(self, obj):
        return obj.forum_answers_by_lesson()


class CourseStats(serializers.ModelSerializer):
    lessons_avg_progress = serializers.SerializerMethodField('get_lessons_avg_progress')

    class Meta:
        model = Course
        fields = ('slug', 'name', 'lessons_avg_progress',)

    @staticmethod
    def get_lessons_avg_progress(obj):
        return obj.avg_lessons_users_progress()