from rest_framework import serializers
from .models import Team, UserTeam
from user.serializers import UserSerializer

class TeamSerializer(serializers.ModelSerializer):
    """队伍序列化器"""
    createUser = UserSerializer(source='userId', read_only=True)
    hasJoinNum = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 
            'name', 
            'description', 
            'maxNum', 
            'expireTime', 
            'userId', 
            'status', 
            'createTime',
            'createUser',
            'hasJoinNum',
            'password'
        ]
        read_only_fields = ['createTime', 'hasJoinNum']

    def get_hasJoinNum(self, obj):
        """获取当前队伍人数"""
        return obj.userteam_set.filter(isDelete=False).count()

    def to_representation(self, instance):
        """自定义序列化输出"""
        data = super().to_representation(instance)
        # 确保日期格式正确
        if data['expireTime']:
            data['expireTime'] = instance.expireTime.strftime('%Y-%m-%dT%H:%M:%S')
        if data['createTime']:
            data['createTime'] = instance.createTime.strftime('%Y-%m-%dT%H:%M:%S')
        return data

class UserTeamSerializer(serializers.ModelSerializer):
    """用户队伍关系序列化器"""
    # 包含用户信息
    user = UserSerializer(source='userId', read_only=True)
    # 包含队伍信息
    team = TeamSerializer(source='teamId', read_only=True)
    
    class Meta:
        model = UserTeam
        fields = [
            'id',
            'userId',
            'teamId',
            'joinTime',
            'createTime',
            'user',
            'team'
        ]
        read_only_fields = ['joinTime', 'createTime']