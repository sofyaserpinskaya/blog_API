from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Post(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=150)
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    publicated = models.BooleanField(default=False)

    class Meta():
        ordering = ('id', )

    def __str__(self):
        return (f'{self.user.username} - {self.title[:20]}'
                f' - {self.pub_date}')
