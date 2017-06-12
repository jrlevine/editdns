from django.test import TestCase, Client
from editapp.models import Domain
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

class EditappTestCase(TestCase):
    def setUp(self):
        """
        make a dummy domain and head
        """
        # make a user
        User.objects.create_user(username='bob',password='zz',email='bob@example.com')
        bob = User.objects.get(username='bob')

        Domain.objects.create(domain="test.com", owner=bob,
            exported=timezone.make_aware(datetime(2000,1,1)),
            rrs="; a comment\nwww A 1.2.3.4")

        # log bob in
        self.c = Client()
        self.c.post('/login/', {'username': 'bob', 'password': 'zz'})


    def test_login(self):
        r2 = self.c.get('/dnsedit')
        print(r2)
        
# test create a domain

# test add record

# test add comment

# test delete record

# test delete comment

# test block edit


