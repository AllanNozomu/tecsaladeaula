import json
import os
import random
import tarfile
from django.http import Http404

from rest_framework import viewsets
import requests

from .models import Answer
from .serializers import AnswerSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    model = Answer
    serializer_class = AnswerSerializer
    filter_fields = ('activity', 'user',)
    lookup_field = 'activity'

    def pre_save(self, obj):
        obj.user = self.request.user

    def get_queryset(self):
        return Answer.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        if 'activity' in self.kwargs:
            activity = self.kwargs['activity']
            try:
                return self.get_queryset().filter(activity=activity).latest('timestamp')
            except Answer.DoesNotExist:
                raise Http404
        return super(AnswerViewSet, self).get_objecct()

    def post_save(self, obj, created):
        if obj.activity.type == "php":
            given = json.loads(obj.given)
            dirname = "%d%d%d" % (obj.user.id, os.getpid(), random.randint(0, 1000))
            os.makedirs("/tmp/%s/" % dirname)
            for f in given:
                fd = open("/tmp/%s/%s" % (dirname, f['name']), 'w')
                fd.write(f['content'])
                fd.close()
            tgz = tarfile.open("/tmp/%s.tgz" % dirname, "w:gz")
            tgz.add("/tmp/%s/" % dirname, arcname="/")
            tgz.close()
            tgz = open("/tmp/%s.tgz" % dirname)
            # TODO colocar no settings.py
            host = 'http://php.timtec.com.br'
            _ = requests.get("%s/%d/start/" % (host, obj.user.id))
            _ = requests.post("%s/%d/documents/" % (host, obj.user.id), files={"tgz": tgz})
