from datetime import datetime
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

#simple object we can use for example purposes
class Comment:
    def __init__(self, email, content, created=None):
        self.email = email
        self.content = content
        self.created = created or datetime.now()

comment = Comment(email='leila@example.com', content='foo bar')


#declare a serializer that we can use to serialize and deserialize data that corresponds to Comment objects.


class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()


#We can now use CommentSerializer to serialize a comment, or list of comments
serializer = CommentSerializer(comment)
#print(serializer.data) 
json = JSONRenderer().render(serializer.data)
  