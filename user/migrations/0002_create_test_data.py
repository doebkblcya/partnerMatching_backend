# user/migrations/xxxx_create_test_data.py
from django.db import migrations
from django.contrib.auth.hashers import make_password
import json

def create_test_data(apps, schema_editor):
    User = apps.get_model('user', 'User')
    
    # 测试用户数据
    test_users = [
        {
            'username': 'user1',
            'password': make_password('123456'),
            'planetCode': 'P001',
            'tags': json.dumps(['Python', '算法', '前端']),
            'profile': '热爱编程，寻找志同道合的伙伴',
            'gender': 1,
            'phone': '13800138001',
            'email': 'user1@example.com',
        },
        {
            'username': 'user2',
            'password': make_password('123456'),
            'planetCode': 'P002',
            'tags': json.dumps(['Java', '后端', '数据库']),
            'profile': '专注后端开发，希望找到学习伙伴',
            'gender': 1,
            'phone': '13800138002',
            'email': 'user2@example.com',
        },
        {
            'username': 'user3',
            'password': make_password('123456'),
            'planetCode': 'P003',
            'tags': json.dumps(['前端', 'Vue', 'React']),
            'profile': '前端开发工程师，寻找项目合作',
            'gender': 0,
            'phone': '13800138003',
            'email': 'user3@example.com',
        },
        {
            'username': 'user4',
            'password': make_password('123456'),
            'planetCode': 'P004',
            'tags': json.dumps(['算法', 'C++', '竞赛']),
            'profile': '算法爱好者，希望找到刷题伙伴',
            'gender': 1,
            'phone': '13800138004',
            'email': 'user4@example.com',
        },
        {
            'username': 'user5',
            'password': make_password('123456'),
            'planetCode': 'P005',
            'tags': json.dumps(['Python', 'AI', '机器学习']),
            'profile': '人工智能研究者，寻找学习伙伴',
            'gender': 0,
            'phone': '13800138005',
            'email': 'user5@example.com',
        },
        {
            'username': 'user6',
            'password': make_password('123456'),
            'planetCode': 'P006',
            'tags': json.dumps(['产品', '设计', 'UI']),
            'profile': '产品经理，寻找技术合作',
            'gender': 0,
            'phone': '13800138006',
            'email': 'user6@example.com',
        },
        {
            'username': 'user7',
            'password': make_password('123456'),
            'planetCode': 'P007',
            'tags': json.dumps(['Java', 'Spring', '微服务']),
            'profile': '全栈开发者，希望交流技术',
            'gender': 1,
            'phone': '13800138007',
            'email': 'user7@example.com',
        },
        {
            'username': 'user8',
            'password': make_password('123456'),
            'planetCode': 'P008',
            'tags': json.dumps(['前端', 'TypeScript', 'Node.js']),
            'profile': '前端架构师，寻找项目合作',
            'gender': 1,
            'phone': '13800138008',
            'email': 'user8@example.com',
        },
    ]
    
    # 创建用户
    for user_data in test_users:
        User.objects.create(**user_data)

def reverse_func(apps, schema_editor):
    User = apps.get_model('user', 'User')
    User.objects.filter(username__startswith='user').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('user', '0001_initial'),  # 确保这里是你的上一个迁移文件
    ]

    operations = [
        migrations.RunPython(create_test_data, reverse_func),
    ]