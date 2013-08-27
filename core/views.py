# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from django.views.generic import DetailView
from django.views.generic.base import TemplateView, View

from models import Course


class HomeView(View):
    def get(self, request):
        latest = Course.objects.latest('publication')
        return redirect(reverse('course_intro', args=[latest.slug]))


class CourseIntroView(DetailView):
    model = Course
    template_name = 'course-intro.html'


def lesson(request):
    return render_to_response('lesson.html')
