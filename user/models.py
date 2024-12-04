from django.db import models
from django.contrib.auth.models import AbstractUser
import json

class User(AbstractUser):
    """用户模型"""
    planetCode = models.CharField(max_length=512, blank=True, verbose_name='星球编号')
    tags = models.JSONField(null=True, blank=True, verbose_name='标签')
    profile = models.TextField(null=True, blank=True, verbose_name='个人简介')
    gender = models.IntegerField(default=0, verbose_name='性别', 
                               choices=((0, '男'), (1, '女')))
    phone = models.CharField(max_length=128, blank=True, verbose_name='电话')
    email = models.EmailField(blank=True, verbose_name='邮箱')
    userStatus = models.IntegerField(default=0, verbose_name='用户状态')
    avatarUrl = models.URLField(max_length=1024, blank=True, verbose_name='头像URL',
                              default='https://gips3.baidu.com/it/u=1004796864,1363400944&fm=3039&app=3039&f=JPEG?w=1024&h=1024')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updateTime = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    isDelete = models.BooleanField(default=False, verbose_name='是否删除')

    def save(self, *args, **kwargs):
        # 确保tags是JSON格式
        if isinstance(self.tags, str):
            try:
                self.tags = json.loads(self.tags)
            except json.JSONDecodeError:
                self.tags = []
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-createTime']

    def __str__(self):
        return f'{self.username}({self.id})'