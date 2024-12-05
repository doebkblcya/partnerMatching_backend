from django.db import models
from user.models import User

class Team(models.Model):
    name = models.CharField(max_length=256, verbose_name='队伍名')
    description = models.TextField(blank=True, verbose_name='队伍描述')
    maxNum = models.IntegerField(default=1, verbose_name='最大人数')
    expireTime = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')
    userId = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')
    status = models.IntegerField(default=0, verbose_name='队伍状态', 
                               choices=((0, '公开'), (1, '私有'), (2, '加密')))
    password = models.CharField(max_length=512, blank=True, verbose_name='密码')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updateTime = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    isDelete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        db_table = 'team'
        verbose_name = '队伍'
        verbose_name_plural = verbose_name
        ordering = ['-createTime']

    def __str__(self):
        return self.name
    
class UserTeam(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    teamId = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='队伍')
    joinTime = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updateTime = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    isDelete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        db_table = 'user_team'
        verbose_name = '用户队伍关系'
        verbose_name_plural = verbose_name
        unique_together = ('userId', 'teamId')  # 一个用户在一个队伍中只能有一条记录

    def __str__(self):
        return f'{self.userId.username} - {self.teamId.name}'