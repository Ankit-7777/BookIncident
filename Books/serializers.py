from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book
from django.contrib.auth.password_validation import validate_password



class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }
    

    def validate(self, data):
        user = self.context['request'].user
        if 'title' in data and not data.get('title'):
            raise serializers.ValidationError({"title": "Title must not be empty."})

        if 'price' in data and data.get('price') <= 0:
            raise serializers.ValidationError({"price": "Price must be a positive number."})

        if 'title' in data and 'author' in data:
            if Book.objects.filter(title=data['title'], author=data['author'], user=user).exists():
                raise serializers.ValidationError("A book with this title and author already exists.")
        return data

    
    

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)




class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password']


    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        validate_password(password)

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

