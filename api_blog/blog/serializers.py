from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Post
        fields = '__all__'
