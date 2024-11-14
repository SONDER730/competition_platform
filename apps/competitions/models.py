# apps/competitions/models.py

from django.db import models

class Competition(models.Model):
    STATUS_CHOICES = [
        (0, "报名未开始"),
        (1, "报名进行中"),
        (2, "报名已结束"),
        (3, "比赛进行中"),
        (4, "比赛已结束"),
    ]

    name = models.CharField(max_length=255, default='无标题')
    link = models.URLField(max_length=500, blank=True)
    type = models.CharField(max_length=100, blank=True)
    reg_time_start = models.DateTimeField(null=True, blank=True)
    reg_time_end = models.DateTimeField(null=True, blank=True)
    comp_time_start = models.DateTimeField(null=True, blank=True)
    comp_time_end = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)  # 新增描述字段
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    def __str__(self):
        return self.name