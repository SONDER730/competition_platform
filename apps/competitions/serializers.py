# apps/competitions/serializers.py

from rest_framework import serializers
from .models import Competition

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = [
            'id',
            'name',
            'link',
            'type',
            'reg_time_start',
            'reg_time_end',
            'comp_time_start',
            'comp_time_end',
            'description',
            'status',
        ]