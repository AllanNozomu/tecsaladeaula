# -*- coding: utf-8 -*-
import json

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView, View, TemplateView
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters
from braces.views import LoginRequiredMixin
from notes.models import Note

from .serializers import (CourseSerializer, CourseProfessorSerializer,
                          CourseThumbSerializer, LessonSerializer,
                          StudentProgressSerializer, CourseNoteSerializer,
                          LessonNoteSerializer, ProfessorMessageSerializer,)

from .models import Course, CourseProfessor, Lesson, StudentProgress, Unit, ProfessorMessage

from forms import ContactForm


class HomeView(ListView):
    context_object_name = 'courses'
    template_name = "home.html"

    def get_queryset(self):
        return Course.objects.all()


class ContactView(View):
    def post(self, request):
        status_code = 200
        contact_form = ContactForm(request.POST)

        if contact_form.is_valid():
            contact_form.send_email()
            content = json.dumps([])
        else:
            status_code = 400
            content = json.dumps(contact_form.errors)

        response = self.options(request)
        response['Content-Type'] = 'application/json'
        response['Content-Length'] = len(content)
        response.content = content
        response.status_code = status_code

        return response


class CourseView(DetailView):
    model = Course
    template_name = 'course.html'

    def get_context_data(self, **kwargs):
        context = super(CourseView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated():
            units_done = StudentProgress.objects.filter(user=user, unit__lesson__course=self.object)\
                                                .exclude(complete=None)\
                                                .values_list('unit', flat=True)
            context['units_done'] = units_done

            user_is_enrolled = self.object.students.filter(id=user.id).exists()
            context['user_is_enrolled'] = user_is_enrolled

        return context


class UserCoursesView(LoginRequiredMixin, TemplateView):
    template_name = 'user-courses.html'


class EnrollCourseView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_object(self):
        if hasattr(self, 'object'):
            return self.object
        self.object = Course.objects.get(**self.kwargs)
        return self.object

    def get_redirect_url(self, **kwargs):
        course = self.get_object()
        course.enroll_student(self.request.user)
        return reverse('lesson', args=[course.slug, course.first_lesson().slug])


class CourseProfessorViewSet(viewsets.ModelViewSet):
    model = CourseProfessor
    lookup_field = 'id'
    filter_fields = ('course', 'user',)
    filter_backends = (filters.DjangoFilterBackend,)
    serializer_class = CourseProfessorSerializer


class ProfessorMessageViewSet(viewsets.ModelViewSet):
    model = ProfessorMessage
    lookup_field = 'id'
    filter_fields = ('course',)
    filter_backends = (filters.DjangoFilterBackend,)
    serializer_class = ProfessorMessageSerializer


class CourseViewSet(viewsets.ModelViewSet):
    model = Course
    lookup_field = 'id'
    filter_fields = ('slug',)
    filter_backends = (filters.DjangoFilterBackend,)
    serializer_class = CourseSerializer

    def get(self, request, **kwargs):
        response = super(CourseViewSet, self).get(request, **kwargs)
        response['Cache-Control'] = 'no-cache'
        return response

    def post(self, request, **kwargs):
        course = self.get_object()
        serializer = CourseSerializer(course, request.DATA)

        if serializer.is_valid():
            serializer.save()
            return Response(status=200)
        else:
            return Response(serializer.errors, status=400)

    def metadata(self, request):
        data = super(CourseViewSet, self).metadata(request)
        data.get('actions').get('POST').get('status').update({'choices': dict(Course.STATES[1:])})
        return data


class CourseThumbViewSet(viewsets.ModelViewSet):
    model = Course
    lookup_field = 'id'
    serializer_class = CourseThumbSerializer

    def post(self, request, **kwargs):
        course = self.get_object()
        serializer = CourseThumbSerializer(course, request.FILES)

        if serializer.is_valid():
            serializer.save()
            return Response(status=200)
        else:
            return Response(serializer.errors, status=400)


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = "lesson.html"

    def get_queryset(self, *args, **kwargs):
        qs = super(LessonDetailView, self).get_queryset(*args, **kwargs)
        course_slug = self.kwargs.get('course_slug')
        return qs.filter(course__slug=course_slug)

    def get_context_data(self, **kwargs):
        context = super(LessonDetailView, self).get_context_data(**kwargs)
        unit_content_type = ContentType.objects.get_for_model(Unit)
        context['unit_content_type_id'] = unit_content_type.id
        return context


class LessonViewSet(viewsets.ModelViewSet):
    model = Lesson
    serializer_class = LessonSerializer
    filter_fields = ('course__slug', 'course__id',)
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    ordering = ('position',)

    def get_queryset(self):
        queryset = super(LessonViewSet, self).get_queryset()
        if self.request.user.is_active:
            return queryset
        return queryset.filter(published=True)


class StudentProgressViewSet(viewsets.ModelViewSet):
    model = StudentProgress
    serializer_class = StudentProgressSerializer
    filter_fields = ('unit', 'unit__lesson',)

    def pre_save(self, obj):
        obj.user = self.request.user
        return super(StudentProgressViewSet, self).pre_save(obj)

    def get_queryset(self):
        user = self.request.user
        return StudentProgress.objects.filter(user=user)


class UpdateStudentProgressView(APIView):
    # fabio: estou desativando esta view
    model = StudentProgress

    def post(self, request, unitId=None):
        user = request.user

        try:
            unit = Unit.objects.get(id=unitId)
        except Unit.DoesNotExist as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response = {}
        progress, created = StudentProgress.objects.get_or_create(user=user, unit=unit)
        progress.complete = timezone.now()
        progress.save()
        response['msg'] = 'Unit completed.'
        response['complete'] = progress.complete
        return Response(response, status=status.HTTP_201_CREATED)


class UserNotesViewSet(LoginRequiredMixin, viewsets.ReadOnlyModelViewSet):

    model = Course
    lookup_field = 'course'

    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        if 'course' in self.kwargs:
            course = get_object_or_404(Course, slug=self.kwargs['course'])
            units = Unit.objects.filter(lesson__course=course, notes__user=user).exclude(notes__isnull=True)

            lessons_dict = {}
            for unit in units:
                lesson = unit.lesson
                if not lesson.slug in lessons_dict:
                    lessons_dict[lesson.slug] = lesson
                    lessons_dict[lesson.slug].units_notes = []
                unit_type = ContentType.objects.get_for_model(unit)
                note = get_object_or_404(Note, user=user, content_type__pk=unit_type.id, object_id=unit.id)
                unit.user_note = note
                lessons_dict[lesson.slug].units_notes.append(unit)

            results = []
            for lesson in lessons_dict.values():
                results.append(LessonNoteSerializer(lesson).data)
            return Response(results)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        units = Unit.objects.filter(notes__user=user).exclude(notes__isnull=True)
        courses = {}
        for unit in units:
            course = unit.lesson.course
            lesson = unit.lesson
            if not course.slug in courses:
                courses[course.slug] = course
                courses[course.slug].lessons_dict = {}
            if not lesson.slug in courses[course.slug].lessons_dict:
                courses[course.slug].lessons_dict[lesson.slug] = lesson
                courses[course.slug].lessons_dict[lesson.slug].units_notes = []
#             unit_type = ContentType.objects.get_for_model(unit)
#             note = get_object_or_404(Note, user=user, content_type__pk=unit_type.id, object_id=unit.id)
#             unit.user_note = note
#             courses[course.slug].lessons_dict[lesson.slug].units_notes.append(unit)

        results = []
        for course in courses.values():
            course.lessons_notes = course.lessons_dict.values()
            del course.lessons_dict
            results.append(CourseNoteSerializer(course).data)
        return Response(results)
