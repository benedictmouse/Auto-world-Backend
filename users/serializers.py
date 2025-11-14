from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        min_length=8
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate password strength
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_approved=False  # Pending approval
        )
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    is_worker = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_staff', 'is_approved', 'is_worker', 'date_joined'
        )
        read_only_fields = ('id', 'email', 'date_joined', 'is_staff', 'is_approved')


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'is_staff', 'is_approved', 'date_joined')


class ApproveUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    approve = serializers.BooleanField(default=True)

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            if user.is_staff:
                raise serializers.ValidationError("Cannot approve/reject admin users.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value


class PromoteToAdminSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            if user.is_staff:
                raise serializers.ValidationError("User is already an admin.")
            if not user.is_approved:
                raise serializers.ValidationError("User must be approved before promotion to admin.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value