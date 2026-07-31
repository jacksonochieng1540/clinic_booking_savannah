from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile, UserActivityLog

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'emergency_contact_name', 'emergency_contact_phone',
            'preferred_language', 'notifications_enabled'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'phone_number', 'role', 'date_of_birth',
            'address', 'profile_picture', 'is_verified',
            'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_verified']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )
    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator()]
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password2',
            'first_name', 'last_name', 'phone_number',
            'role', 'date_of_birth', 'address'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': "Password fields didn't match."
            })
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': "A user with this email already exists."
            })
        
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({
                'username': "A user with this username already exists."
            })
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        
        request = self.context.get('request')
        if request:
            UserActivityLog.objects.create(
                user=user,
                action='register',
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'error': 'Invalid email or password'
                })
            
            user = authenticate(username=user.username, password=password)
            
            if not user:
                raise serializers.ValidationError({
                    'error': 'Invalid email or password'
                })
            
            if not user.is_active:
                raise serializers.ValidationError({
                    'error': 'This account is deactivated'
                })
            
            refresh = RefreshToken.for_user(user)
            
            request = self.context.get('request')
            if request:
                UserActivityLog.objects.create(
                    user=user,
                    action='login',
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )
            
            attrs['user'] = user
            attrs['refresh'] = str(refresh)
            attrs['access'] = str(refresh.access_token)
            
            return attrs
        else:
            raise serializers.ValidationError({
                'error': 'Email and password are required'
            })


class UserLogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)
    
    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        
        if not refresh_token:
            raise serializers.ValidationError({
                'error': 'Refresh token is required'
            })
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            raise serializers.ValidationError({
                'error': str(e)
            })
        
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password': "Password fields didn't match."
            })
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password': "Password fields didn't match."
            })
        return attrs


class UserActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserActivityLog
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'action', 'ip_address', 'user_agent',
            'details', 'created_at'
        ]
        read_only_fields = ['created_at']