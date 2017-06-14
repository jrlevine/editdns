from django.test import TestCase, Client
from .models import Domain
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

        Domain.objects.create(domain="HEAD", owner=bob,
            exported=timezone.make_aware(datetime(2000,1,1)),
            rrs="""; common head records for zones
   3600 SOA ns1.example.com hostmaster.example.com. 99999 3600 3600 3600 3600
   3600 NS ns1.example.com.
   NS ns2.example.com.""")

        # log bob in
        self.c = Client()
        self.c.post('/login/', {'username': 'bob', 'password': 'zz'})

# make sure we're really logged in
    def test_01login(self):
        resp = self.c.get('/edit')
        self.assertIn('/edit/test.com', resp.content.decode())
        self.assertNotIn('/login/', resp.content.decode())
        
# test create a domain
    def test_02create(self):
        rc = self.c.post('/edit/create', {"domain": "test.test", "owner": "bob" })
        self.assertIn('records for test.test', rc.content.decode())

# test add record
    def test_03addrecord(self):
        # get the record form
        rc = self.c.post('/edit/recadd/test.com', {"rrname": "A" })
        self.assertIn('input type="text" name="rrname" value="A"', rc.content.decode())

        # add the record
        rc = self.c.post('/edit/recadd/test.com', {"rrname": "A", "rrname0": "A",
            "name": "", "ttl": "100", "rr0": "11.22.33.44" })
        self.assertIn('100 A 11.22.33.44', rc.content.decode())

# test edit comment
    def test_04editrecord(self):
        # get the record form
        rc = self.c.get('/edit/record/test.com/0')
        self.assertIn('Comment:', rc.content.decode())
        self.assertIn('a comment', rc.content.decode())

        # update it
        rc = self.c.post('/edit/record/test.com/0', {"comment": "; different comment", "rrname0": "COMMENT"})
        self.assertIn('different comment', rc.content.decode())

# test delete record
    def test_05deleterecord(self):
        # get the record form
        rc = self.c.get('/edit/record/test.com/0')
        self.assertIn('Comment:', rc.content.decode())
        self.assertIn('a comment', rc.content.decode())

        rc = self.c.post('/edit/record/test.com/0', {"comment": "; different comment", "rrname0": "COMMENT",
            "delete": "Delete"})
        self.assertNotIn('a comment', rc.content.decode())

# test block edit
    def test_06blockedit(self):
        # get the record form
        rc = self.c.post('/edit/edit/test.com', {"block": "Block edit"})
        self.assertIn("www A 1.2.3.4", rc.content.decode())

    def test_07blockchange(self):
        # change it
        rc = self.c.post('/edit/editblock/test.com', {"domain": "test.com", "owner": "bob",
            "rrs": "; a comment\n MX 10 mail\nwww A 1.2.3.4"})
        self.assertIn(" MX 10 mail", rc.content.decode())

    def test_08badedit(self):
        # bad record
        rc = self.c.post('/edit/editblock/test.com', {"domain": "test.com", "owner": "bob",
            "rrs": "; a comment\n 10 A 1.2.3\nwww A 1.2.3.4"})
        self.assertIn("Bad IPv4 format", rc.content.decode())

