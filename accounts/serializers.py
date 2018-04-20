from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import CourseStudent, Course

from .models import City, Occupation, Discipline, EducationDegree, EducationLevel, School, TimtecUserSchool


class TimtecUserSerializer(serializers.ModelSerializer):
    name = serializers.Field(source='get_full_name')
    picture = serializers.Field(source='get_picture_url')

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'name', 'first_name', 'last_name', 'biography', 'picture',)


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City

class OccupationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Occupation

class DisciplineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Discipline

class EducationDegreeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EducationDegree

class EducationLevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = EducationLevel

class SchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School

class SchoolCompleteSerializer(serializers.ModelSerializer):
    city = CitySerializer(required=True)
    school_type_complete = serializers.SerializerMethodField('get_school_type_complete')

    class Meta:
        model = School

    def get_school_type_complete(self, obj):
        return obj.get_school_type_display()

class TimtecUserSchoolSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(required=True)

    class Meta:
        model = TimtecUserSchool

class TimtecProfileSchoolSerializer(serializers.ModelSerializer):
    school = SchoolCompleteSerializer(required=True)
    education_levels = EducationLevelSerializer(many=True, required=True)

    class Meta:
        model = TimtecUserSchool

class TimtecProfileSerializer(serializers.ModelSerializer):
    city = CitySerializer(required=False)
    occupations = OccupationSerializer(many=True, required=False)
    disciplines = DisciplineSerializer(many=True, required=False)
    education_degrees = EducationDegreeSerializer(required=False, many=True)
    schools = TimtecProfileSchoolSerializer(source='timtecuserschool_set', many=True)

    class Meta:
        model = get_user_model()
        fields = ('city', 'occupations', 'disciplines', 'education_degrees', 'schools')

class CourseProgressSerializer(serializers.ModelSerializer):
    course_progress = serializers.SerializerMethodField('get_course_progress')
    name = serializers.SerializerMethodField('get_course_name')

    class Meta:
        model = CourseStudent
        fields = ('course_progress', 'name',)

    def get_course_progress(self, obj):
        return obj.percent_progress()

    def get_course_name(self, obj):
        return obj.course.name

class TimtecUserAdminSerializer(TimtecUserSerializer):
    city = CitySerializer(read_only=True)
    occupations = OccupationSerializer(many=True, read_only=True)
    disciplines = DisciplineSerializer(many=True, read_only=True)
    education_degrees = EducationDegreeSerializer(many=True, read_only=True)
    schools = TimtecProfileSchoolSerializer(source='timtecuserschool_set', many=True, read_only=True)
    courses = serializers.SerializerMethodField('get_courses')

    class Meta:
        model = get_user_model()
        fields =    ('id', 'username', 'name', 'email', 'business_email', 'is_active', 'is_superuser', 'first_name', 'city',
                    'occupations', 'disciplines', 'education_degrees', 'schools', 'courses', 'site', 'biography')

    def get_courses(self, obj):
        course_students = CourseStudent.objects.filter(user=obj.id)
        course_student_progress = [CourseProgressSerializer(cs).data for cs in course_students]
        
        return course_student_progress