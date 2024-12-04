# user/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from .serializers import UserSerializer
from .models import User
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.db.models import Q

class UserLoginView(APIView):
    permission_classes = []  # 登录接口不需要认证
    authentication_classes = []  # 登录接口不需要认证

    def post(self, request):
        userAccount = request.data.get('userAccount')
        userPassword = request.data.get('userPassword')
        
        try:
            user = User.objects.get(username=userAccount)
            if user.check_password(userPassword):
                login(request, user)
                return Response({
                    'code': 0,
                    'data': UserSerializer(user).data
                })
            else:
                return Response({
                    'code': 40000,
                    'data': None,
                    'message': '密码错误'
                })
        except User.DoesNotExist:
            return Response({
                'code': 40000,
                'data': None,
                'message': '用户不存在'
            })

@method_decorator(csrf_exempt, name='dispatch')
class UserLogoutView(APIView):
    authentication_classes = []  # 移除认证要求
    permission_classes = []      # 移除权限要求
    
    def post(self, request):
        try:
            logout(request)
            return Response({
                'code': 0,
                'data': None,
                'message': '退出成功'
            })
        except Exception as e:
            return Response({
                'code': 40000,
                'data': None,
                'message': str(e)
            })

class UserAccountExistView(APIView):
    authentication_classes = []  # 不需要认证
    permission_classes = []      # 不需要权限

    def post(self, request):
        userAccount = request.data.get('userAccount')
        # 检查用户名是否存在
        exists = User.objects.filter(username=userAccount).exists()
        return Response({
            'code': 0,
            'date': exists,
            'message': '用户名已存在' if exists else '用户名可用'
        })

class UserRegisterView(APIView):
    authentication_classes = []  # 不需要认证
    permission_classes = []      # 不需要权限

    def post(self, request):
        try:
            data = request.data
            userAccount = data.get('userAccount')
            userPassword = data.get('userPassword')
            checkPassword = data.get('checkPassword')
            
            # 基本验证
            if not userAccount or not userPassword:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '用户名或密码不能为空'
                })
            
            if userPassword != checkPassword:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '两次输入的密码不一致'
                })
            
            # 创建用户
            user = User.objects.create_user(
                username=userAccount,
                password=userPassword,
                email=data.get('email'),
                phone=data.get('phone'),
                gender=data.get('gender', 1),
                # 使用userAccount作为username，使用传入的username作为昵称
                first_name=data.get('username')  # 用first_name存储昵称
            )
            
            # 返回用户id
            return Response({
                'code': 0,
                'date': user.id,
                'message': '注册成功'
            })
            
        except Exception as e:
            return Response({
                'code': 40000,
                'date': None,
                'message': str(e)
            })
        
class CurrentUserView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            return Response({
                'code': 0,
                'date': {
                    'id': user.id,
                    'username': user.username,
                    'userAccount': user.username,  # 使用username作为userAccount
                    'avatarUrl': 'https://gips3.baidu.com/it/u=1004796864,1363400944&fm=3039&app=3039&f=JPEG?w=1024&h=1024',  # 默认头像
                    'gender': user.gender,
                    'phone': user.phone,
                    'email': user.email,
                    'planetCode': user.planetCode,
                    'createTime': user.createTime.strftime('%Y-%m-%d %H:%M:%S') if user.createTime else None,
                    'tags': user.tags,
                }
            })
        return Response({
            'code': 40100,
            'date': None,
            'message': '未登录'
        })

class UserRecommendView(APIView):
    def get(self, request):
        try:
            # 获取分页参数
            page_size = int(request.GET.get('pageSize', 8))
            page_num = int(request.GET.get('pageNum', 1))
            
            # 获取活跃用户
            users = User.objects.filter(is_active=True).exclude(id=request.user.id)
            
            # 分页
            paginator = Paginator(users, page_size)
            current_page = paginator.page(page_num)
            
            # 序列化
            user_data = UserSerializer(current_page.object_list, many=True).data
            
            return Response({
                'code': 0,
                'date': {  # 注意：前端代码中使用的是 date 而不是 data
                    'records': user_data,
                    'total': paginator.count,
                    'pages': paginator.num_pages,
                    'current': page_num
                }
            })
        except Exception as e:
            return Response({
                'code': 40000,
                'message': '获取推荐用户失败',
                'description': str(e)
            })

class UserMatchView(APIView):
    def get(self, request):
        try:
            num = int(request.GET.get('num', 10))
            current_user = request.user
            
            # 获取当前用户的标签
            current_user_tags = current_user.tags if current_user.tags else []
            
            # 获取其他用户
            users = User.objects.filter(is_active=True).exclude(id=current_user.id)
            
            # 如果有标签，进行标签匹配
            if current_user_tags:
                # 这里可以实现更复杂的标签匹配算法
                matched_users = []
                for user in users:
                    user_tags = user.tags if user.tags else []
                    if set(current_user_tags) & set(user_tags):  # 标签有交集的用户
                        matched_users.append(user)
                users = matched_users[:num]
            else:
                # 如果没有标签，随机返回用户
                users = users.order_by('?')[:num]
            
            return Response({
                'code': 0,
                'date': UserSerializer(users, many=True).data
            })
        except Exception as e:
            return Response({
                'code': 40000,
                'message': '获取匹配用户失败',
                'description': str(e)
            })
    
class UserUpdateView(APIView):
    def post(self, request):
        try:
            # 获取要更新的用户ID和字段
            user_id = request.data.get('id')
            
            # 验证用户存在性
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '用户不存在'
                })
            
            # 确保只能更新自己的信息
            if request.user.id != user_id:
                return Response({
                    'code': 40100,
                    'date': None,
                    'message': '无权限修改他人信息'
                })
            
            # 可更新的字段列表
            allowed_fields = {
                'username': 'first_name',  # username存储在first_name中
                'gender': 'gender',
                'phone': 'phone',
                'email': 'email',
                'profile': 'profile',
                'avatarUrl': 'avatarUrl'
            }
            
            # 更新字段
            updated = False
            for field, model_field in allowed_fields.items():
                if field in request.data:
                    value = request.data.get(field)
                    if field == 'gender':
                        value = int(value)  # 确保性别是整数
                    setattr(user, model_field, value)
                    updated = True
            
            if updated:
                user.save()
                return Response({
                    'code': 0,
                    'date': 1,  # 前端期望大于0的值表示成功
                    'message': '更新成功'
                })
            else:
                return Response({
                    'code': 40000,
                    'date': 0,
                    'message': '未更新任何字段'
                })
                
        except Exception as e:
            return Response({
                'code': 40000,
                'date': 0,
                'message': str(e)
            })

class UserTagSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            print("Raw request GET params:", request.GET)
            tag_list = request.GET.getlist('tagNameList', [])
            
            if not tag_list:
                tag_list = request.GET.getlist('tagNameList[]', [])
            
            print("Searching with tags:", tag_list)
            
            if not tag_list:
                return Response({
                    'code': 0,
                    'date': [],
                    'message': '标签参数为空'
                })

            # 获取所有活跃用户
            users = User.objects.filter(is_active=True)
            
            # 根据标签筛选
            for tag in tag_list:
                if tag == '男':
                    users = users.filter(gender=0)
                elif tag == '女':
                    users = users.filter(gender=1)
                else:
                    # 对于其他标签，检查JSON字段中是否包含该标签
                    filtered_users = []
                    for user in users:
                        if user.tags:  # 确保用户有标签
                            user_tags = user.tags if isinstance(user.tags, list) else json.loads(user.tags)
                            if tag in user_tags:
                                filtered_users.append(user.id)
                    users = users.filter(id__in=filtered_users)

            print(f"Found {users.count()} users")
            
            # 序列化结果
            user_list = []
            for user in users:
                user_data = UserSerializer(user).data
                # 确保tags是列表格式
                if user_data.get('tags'):
                    if isinstance(user_data['tags'], str):
                        user_data['tags'] = json.loads(user_data['tags'])
                print(f"Adding user to results: {user.username}, gender: {user.gender}, tags: {user_data['tags']}")
                user_list.append(user_data)

            return Response({
                'code': 0,
                'date': user_list,
                'message': '搜索成功'
            })
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response({
                'code': 40000,
                'date': [],
                'message': str(e)
            })