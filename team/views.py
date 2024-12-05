from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import Team, UserTeam
from .serializers import TeamSerializer
import datetime
from django.core.paginator import Paginator
from django.db.models import Q

class TeamAddView(APIView):
    def post(self, request):
        try:
            print("Received data:", request.data)
            data = request.data.copy()
            
            # 检查用户是否登录
            if not request.user.is_authenticated:
                return Response({
                    'code': 40100,
                    'date': None,
                    'message': '用户未登录'
                })
            
            # 创建队伍数据
            team_data = {
                'name': data['name'],
                'description': data['description'],
                'expireTime': data['expireTime'],
                'maxNum': int(data['maxNum']),
                'password': data.get('password', ''),
                'status': int(data['status']),
                'userId': request.user.id  # 使用用户ID而不是用户对象
            }
            
            # 验证过期时间
            if team_data['expireTime']:
                try:
                    expire_time = datetime.datetime.fromisoformat(team_data['expireTime'])
                    if expire_time < timezone.now():
                        return Response({
                            'code': 40000,
                            'date': None,
                            'message': '过期时间不能早于当前时间'
                        })
                except Exception as e:
                    return Response({
                        'code': 40000,
                        'date': None,
                        'message': '过期时间格式错误'
                    })
            
            # 验证人数
            if not (3 <= team_data['maxNum'] <= 10):
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '队伍人数必须在3-10人之间'
                })
            
            # 验证加密队伍必须设置密码
            if team_data['status'] == 2 and not team_data['password']:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '加密房间必须设置密码'
                })
            
            print("Creating team with data:", team_data)
            serializer = TeamSerializer(data=team_data)
            if serializer.is_valid():
                team = serializer.save()
                
                # 创建者加入队伍
                UserTeam.objects.create(
                    userId=request.user,
                    teamId=team
                )
                
                return Response({
                    'code': 0,
                    'date': serializer.data,
                    'message': '创建成功'
                })
            else:
                print("Serializer errors:", serializer.errors)
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': str(serializer.errors)
                })
                
        except Exception as e:
            import traceback
            print("Error:", str(e))
            print("Traceback:", traceback.format_exc())
            return Response({
                'code': 40000,
                'date': None,
                'message': str(e)
            })
        
class TeamListView(APIView):
    def get(self, request):
        try:
            # 获取请求参数
            search_text = request.GET.get('searchText', '')
            status = int(request.GET.get('status', 0))  # 0-公开，2-加密
            
            # 构建查询条件
            query = Q(isDelete=False)
            
            # 状态过滤
            query &= Q(status=status)
            
            # 搜索过滤
            if search_text:
                query &= (Q(name__icontains=search_text) | 
                         Q(description__icontains=search_text))
            
            # 过期时间过滤
            query &= (Q(expireTime__isnull=True) | 
                     Q(expireTime__gt=timezone.now()))
            
            # 执行查询
            teams = Team.objects.filter(query).order_by('-createTime')
            
            # 序列化
            team_list = []
            for team in teams:
                team_data = TeamSerializer(team).data
                # 获取队伍当前人数
                team_data['hasJoinNum'] = team.userteam_set.filter(isDelete=False).count()
                # 添加当前用户是否已加入
                if request.user.is_authenticated:
                    team_data['hasJoin'] = UserTeam.objects.filter(
                        userId=request.user,
                        teamId=team,
                        isDelete=False
                    ).exists()
                else:
                    team_data['hasJoin'] = False
                team_list.append(team_data)
            
            return Response({
                'code': 0,
                'date': team_list,
                'message': '获取成功'
            })
            
        except Exception as e:
            print(f"List team error: {str(e)}")
            return Response({
                'code': 40000,
                'date': [],
                'message': str(e)
            })


class TeamListMyJoinView(APIView):
    def get(self, request):
        try:
            # 检查用户是否登录
            if not request.user.is_authenticated:
                return Response({
                    'code': 40100,
                    'date': None,
                    'message': '用户未登录'
                })

            # 获取搜索参数
            search_text = request.GET.get('searchText', '')
            
            # 获取用户加入的所有队伍ID
            user_team_ids = UserTeam.objects.filter(
                userId=request.user,
                isDelete=False
            ).values_list('teamId', flat=True)
            
            # 构建查询条件
            query = Q(id__in=user_team_ids, isDelete=False)
            
            # 搜索过滤
            if search_text:
                query &= (Q(name__icontains=search_text) | 
                         Q(description__icontains=search_text))
            
            # 过期时间过滤
            query &= (Q(expireTime__isnull=True) | 
                     Q(expireTime__gt=timezone.now()))
            
            # 执行查询
            teams = Team.objects.filter(query).order_by('-createTime')
            
            # 序列化
            team_list = []
            for team in teams:
                team_data = TeamSerializer(team).data
                team_data['hasJoinNum'] = team.userteam_set.filter(isDelete=False).count()
                team_data['hasJoin'] = True  # 这是用户加入的队伍列表，所以一定是已加入的
                team_list.append(team_data)
            
            return Response({
                'code': 0,
                'date': team_list,
                'message': '获取成功'
            })
            
        except Exception as e:
            print(f"List my join teams error: {str(e)}")
            return Response({
                'code': 40000,
                'date': [],
                'message': str(e)
            })


class TeamJoinView(APIView):
    def post(self, request):
        try:
            # 检查用户是否登录
            if not request.user.is_authenticated:
                return Response({
                    'code': 40100,
                    'date': None,
                    'message': '用户未登录'
                })

            # 获取参数
            team_id = request.data.get('teamId')
            password = request.data.get('password', '')

            print(f"Attempting to join team {team_id} with password: {password}")

            # 查询队伍
            try:
                team = Team.objects.get(id=team_id, isDelete=False)
            except Team.DoesNotExist:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '队伍不存在'
                })

            # 检查队伍是否过期
            if team.expireTime and team.expireTime < timezone.now():
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '队伍已过期'
                })

            # 检查是否已加入
            existing_membership = UserTeam.objects.filter(
                userId=request.user,
                teamId=team
            ).first()
            
            if existing_membership:
                if not existing_membership.isDelete:
                    # 如果有未删除的记录，说明用户已是成员
                    return Response({
                        'code': 40000,
                        'date': None,
                        'message': '你已经是队伍成员了'
                    })
                else:
                    # 如果是已退出的记录，检查是否可以重新加入
                    # 检查队伍人数
                    current_num = UserTeam.objects.filter(
                        teamId=team,
                        isDelete=False
                    ).count()
                    
                    if current_num >= team.maxNum:
                        return Response({
                            'code': 40000,
                            'date': None,
                            'message': '队伍已满'
                        })
                    
                    # 检查加密队伍密码
                    if team.status == 2:
                        if not password:
                            return Response({
                                'code': 40000,
                                'date': None,
                                'message': '请输入密码'
                            })
                        if password != team.password:
                            return Response({
                                'code': 40000,
                                'date': None,
                                'message': '密码错误'
                            })
                    
                    # 重新激活记录
                    existing_membership.isDelete = False
                    existing_membership.save()
                    return Response({
                        'code': 0,
                        'date': True,
                        'message': '加入成功'
                    })

            # 检查队伍人数限制
            current_num = UserTeam.objects.filter(
                teamId=team,
                isDelete=False
            ).count()
            
            if current_num >= team.maxNum:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '队伍已满'
                })

            # 检查用户加入的队伍数量限制
            user_team_count = UserTeam.objects.filter(
                userId=request.user,
                isDelete=False
            ).count()
            
            if user_team_count >= 5:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '最多加入5个队伍'
                })

            # 检查队伍状态和密码
            if team.status == 2:  # 加密
                if not password:
                    return Response({
                        'code': 40000,
                        'date': None,
                        'message': '请输入密码'
                    })
                if password != team.password:
                    return Response({
                        'code': 40000,
                        'date': None,
                        'message': '密码错误'
                    })
            elif team.status == 1:  # 私有
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '禁止加入私有队伍'
                })

            # 创建新的加入记录
            UserTeam.objects.create(
                userId=request.user,
                teamId=team
            )

            print(f"Successfully joined team {team_id}")

            return Response({
                'code': 0,
                'date': True,
                'message': '加入成功'
            })

        except Exception as e:
            print(f"Join team error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response({
                'code': 40000,
                'date': None,
                'message': str(e)
            })

class TeamListMyCreateView(APIView):
    def get(self, request):
        try:
            # 检查用户是否登录
            if not request.user.is_authenticated:
                return Response({
                    'code': 40100,
                    'date': None,
                    'message': '用户未登录'
                })

            # 获取搜索参数
            search_text = request.GET.get('searchText', '')
            
            # 构建查询条件
            query = Q(userId=request.user, isDelete=False)
            
            # 搜索过滤
            if search_text:
                query &= (Q(name__icontains=search_text) | 
                         Q(description__icontains=search_text))
            
            # 过期时间过滤（可选，看是否需要显示已过期的队伍）
            # query &= (Q(expireTime__isnull=True) | 
            #          Q(expireTime__gt=timezone.now()))
            
            # 执行查询
            teams = Team.objects.filter(query).order_by('-createTime')
            
            # 序列化
            team_list = []
            for team in teams:
                team_data = TeamSerializer(team).data
                team_data['hasJoinNum'] = team.userteam_set.filter(isDelete=False).count()
                team_data['hasJoin'] = True  # 创建者也是队伍成员
                team_list.append(team_data)
            
            return Response({
                'code': 0,
                'date': team_list,
                'message': '获取成功'
            })
            
        except Exception as e:
            print(f"List my create teams error: {str(e)}")
            return Response({
                'code': 40000,
                'date': [],
                'message': str(e)
            })

# 添加退出队伍的视图
class TeamQuitView(APIView):
    def post(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({
                    'code': 40100,
                    'date': None,
                    'message': '用户未登录'
                })

            team_id = request.data.get('teamId')
            if not team_id:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '队伍不存在'
                })

            # 查找用户的队伍关系
            user_team = UserTeam.objects.filter(
                userId=request.user,
                teamId=team_id,
                isDelete=False
            ).first()

            if not user_team:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '未加入该队伍'
                })

            # 不能退出自己创建的队伍
            if user_team.teamId.userId == request.user:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '创建者不能退出队伍'
                })

            # 软删除用户队伍关系
            user_team.isDelete = True
            user_team.save()

            return Response({
                'code': 0,
                'date': True,
                'message': '退出成功'
            })

        except Exception as e:
            print(f"Quit team error: {str(e)}")
            return Response({
                'code': 40000,
                'date': None,
                'message': str(e)
            })

# 添加解散队伍的视图
class TeamDeleteView(APIView):
    def post(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({
                    'code': 40100,
                    'date': None,
                    'message': '用户未登录'
                })

            team_id = request.data.get('id')
            if not team_id:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '队伍不存在'
                })

            # 查找队伍
            team = Team.objects.filter(
                id=team_id,
                userId=request.user,
                isDelete=False
            ).first()

            if not team:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '队伍不存在或无权限'
                })

            # 软删除队伍
            team.isDelete = True
            team.save()

            # 软删除所有队伍关系
            UserTeam.objects.filter(teamId=team).update(isDelete=True)

            return Response({
                'code': 0,
                'date': True,
                'message': '解散成功'
            })

        except Exception as e:
            print(f"Delete team error: {str(e)}")
            return Response({
                'code': 40000,
                'date': None,
                'message': str(e)
            })

class TeamGetView(APIView):
    def get(self, request):
        try:
            # 获取队伍ID
            team_id = request.GET.get('id')
            if not team_id:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '队伍不存在'
                })

            # 查询队伍
            try:
                team = Team.objects.get(id=team_id, isDelete=False)
            except Team.DoesNotExist:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '队伍不存在'
                })

            # 检查权限（只有创建者可以查看完整信息）
            if team.userId != request.user:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '无权限'
                })

            # 序列化
            team_data = TeamSerializer(team).data
            
            return Response({
                'code': 0,
                'date': team_data,
                'message': '获取成功'
            })

        except Exception as e:
            print(f"Get team error: {str(e)}")
            return Response({
                'code': 40000,
                'date': None,
                'message': str(e)
            })

class TeamUpdateView(APIView):
    def post(self, request):
        try:
            data = request.data
            team_id = data.get('id')

            # 查询队伍
            try:
                team = Team.objects.get(id=team_id, isDelete=False)
            except Team.DoesNotExist:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '队伍不存在'
                })

            # 检查权限
            if team.userId != request.user:
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '无权限'
                })

            # 验证过期时间
            if data.get('expireTime'):
                expire_time = datetime.datetime.fromisoformat(data['expireTime'])
                if expire_time < timezone.now():
                    return Response({
                        'code': 40000,
                        'date': None,
                        'message': '过期时间不能早于当前时间'
                    })

            # 验证加密队伍必须设置密码
            if int(data['status']) == 2 and not data.get('password'):
                return Response({
                    'code': 40000,
                    'date': None,
                    'message': '加密房间必须设置密码'
                })

            # 更新字段
            update_fields = ['name', 'description', 'expireTime', 'status']
            for field in update_fields:
                if field in data:
                    setattr(team, field, data[field])
            
            # 特殊处理密码字段
            if 'password' in data:
                team.password = data['password']

            # 保存更新
            team.save()

            return Response({
                'code': 0,
                'date': True,
                'message': '更新成功'
            })

        except Exception as e:
            print(f"Update team error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response({
                'code': 40000,
                'date': None,
                'message': str(e)
            })