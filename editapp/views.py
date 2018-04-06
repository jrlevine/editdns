# DNS editor views

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Substr
from django.utils import timezone
from .forms import DomainForm, ShortDomainForm, DomainEditForm
from .formsextlang import extxl, RRForm, CommentForm
from .models import Domain
from django.contrib.auth.models import User
from datetime import datetime
import dnsextlang

@login_required
def indexview(request):
    """
    initial page
    shows all the domains in columns
    """

    domdb = Domain.objects
    if not request.user.has_perm('editapp.see_all'): # only see mine
        domdb = domdb.filter(owner__username=request.user.username)
    domains = [ d.domain for d in domdb.order_by('domain') ]

    # show in four columns
    # so slice into four arrays
    dslice = int((len(domains)+3)/4)
    c1,c2,c3,c4 = [ [d for d in domains[n*dslice:(n+1)*dslice]] for n in range(4) ]

    return render(request, 'editapp/index.html',
        {
            'c1': c1, 'c2': c2, 'c3': c3, 'c4': c4,
            'bpnav': bpnav(request, 'index')
        })

@login_required
def createview(request):
    """
    create new domain
    """
    if request.method == 'POST':
        form = ShortDomainForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            owner = cd['owner'] if cd['owner'] else request.user.username
            ownerdb = User.objects.get(username=owner)
            domainname = cd['domain']

            # see if it's a duplicate name
            exists = Domain.objects.filter(domain=domainname)
            if len(exists) == 0:
                Domain.objects.create(domain=domainname,
                    owner=ownerdb,
                    exported=timezone.make_aware(datetime(2000,1,1)),
                    rrs='; records for {0}\n'.format(domainname))
                return editview(request, domainname)
            # duplicate name
            form.errors["domain"] = ["Name already exists"]
        # otherwise fall through to try again
    else:
        form = ShortDomainForm(initial={'owner': request.user.username })
    return render(request, 'editapp/create.html',
        {
            'form': form,
            'bpnav': bpnav(request, 'create')
        })

@login_required
def editblockview(request, domainname, postok=True):
    """
    edit existing domain as a block of text
    argument is domain name
    """

    # has to exist if you're going to edit it
    if request.user.has_perm('dnsedit.see_all'): # only see mine ?
        dom = get_object_or_404(Domain, domain=domainname) 
    else:
        dom = get_object_or_404(Domain, domain=domainname, owner__username=request.user.username)

    if postok and request.method == 'POST':
        form = DomainForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            owner = cd['owner'] if cd['owner'] else request.user.username # non-priv can't change owner
            ownerdb = User.objects.get(username=owner)

            dom.ownerdb = ownerdb
            dom.rrs=cd['rrs']
            dom.updated = timezone.now()
            dom.save()
            return editview(request, domainname, postok=False)
        # otherwise fall through to edit again
    else:
        form = DomainForm(initial={'domain': dom.domain, 'owner': dom.owner.username, 'rrs': dom.rrs})

    return render(request, 'editapp/editblock.html',
        {
            'form': form,
            'domain': domainname,
            'bpnav': bpnav(request, 'edit')
        })

def editview(request, domainname, postok=True):
    """
    edit existing domain as records
    argument is domain name
    """

    # has to exist if you're going to edit it
    if request.user.has_perm('dnsedit.see_all'): # only see mine ?
        dom = get_object_or_404(Domain, domain=domainname) 
    else:
        dom = get_object_or_404(Domain, domain=domainname, owner__username=request.user.username)

    if postok and request.method == 'POST':
        if 'block' in request.POST:      # block edit button
            return editblockview(request, domainname, postok=False)

        form = DomainEditForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            owner = cd['owner'] if cd['owner'] else request.user.username # non-priv can't change owner
            ownerdb = User.objects.get(username=owner)

            dom.ownerdb = ownerdb
            dom.updated = timezone.now()
            # post doesn't change records, only maybe the owner
            dom.updated = timezone.now()
            dom.save()
        # otherwise fall through to edit again
    else:
        form = DomainEditForm(initial={'domain': dom.domain, 'owner': dom.owner.username })

    # make records individually editable
    rrls = dnsextlang.ExtrecList(extxl, dom.rrs)
    # list of (seq, valid, rrtext
    rrview = [ (n, r.is_valid(), str(r)) for n, r in enumerate(rrls, start=0) ]

    # spinner for new RRs
    addspinner = extxl.rrnames(select="rrname")

    return render(request, 'editapp/edit.html',
        {
            'form': form,
            'domain': domainname,
            'rrview': rrview,
            'addspinner': addspinner,
            'bpnav': bpnav(request, 'edit')
        })

@login_required
def recordview(request, domainname, recno):
    """
    edit or delete a record existing domain as a block of text
    argument is domain name, record number
    """

    # has to exist if you're going to edit it
    if request.user.has_perm('dnsedit.see_all'): # only see mine ?
        dom = get_object_or_404(Domain, domain=domainname) 
    else:
        dom = get_object_or_404(Domain, domain=domainname, owner__username=request.user.username)
    lineno = int(recno)
    rrs = dnsextlang.ExtrecList(extxl, dom.rrs)
    if lineno < 0 or lineno > len(rrs):
        raise Http404("No record {0} in {1}".format(lineno, domainname))

    if request.method == 'POST':
        if request.POST['rrname0'] == "COMMENT":
            form = CommentForm(request.POST)
            if form.is_valid():
                rrlist = dom.rrs.splitlines()
                if 'delete' in request.POST:
                    rrlist[lineno:lineno+1] = [] # snip out the record
                else:
                    rrlist[lineno] = form.cleaned_data.get('comment')
                dom.rrs = "\n".join(rrlist)
                dom.updated = timezone.now()
                dom.save()
                return editview(request, domainname, postok=False)
        else:
            form = RRForm(request.POST)
            if form.is_valid():
                rrlist = dom.rrs.splitlines()
                if 'delete' in request.POST:
                    rrlist[lineno:lineno+1] = [] # snip out the record
                else:
                    rrlist[lineno] = form.cleaned_data.get('dnsrecord')
                dom.rrs = "\n".join(rrlist)
                dom.updated = timezone.now()
                dom.save()
                return editview(request, domainname, postok=False)

        # otherwise fall through to edit again

    else:    
        record = str(rrs[lineno])
        if record.strip()[0] == ';':     # it's a comment
            form = CommentForm(initial={'comment': record})
        else:
            form = RRForm(record)
    
    return render(request, 'editapp/record.html',
        {
            'form': form,
            'domain': domainname,
            'recno': recno,
            'bpnav': bpnav(request, 'edit')
        })

@login_required
def recordaddview(request, domainname):
    """
    add a new a record existing domain as a block of text
    argument is domain name, post argument rrname is rrname
    """

    # has to exist if you're going to edit it
    if request.user.has_perm('dnsedit.see_all'): # only see mine ?
        dom = get_object_or_404(Domain, domain=domainname) 
    else:
        dom = get_object_or_404(Domain, domain=domainname, owner__username=request.user.username)

    if request.method == 'POST' and 'rrname0' in request.POST: # edited form rather than Add button
        if request.POST['rrname0'] == "COMMENT":
            form = CommentForm(request.POST)
            if form.is_valid():
                rrlist = dom.rrs.splitlines()
                rrlist.append(form.cleaned_data.get('comment'))
                dom.rrs = "\n".join(rrlist)
                dom.updated = timezone.now()
                dom.save()
                return editview(request, domainname, postok=False)
        else:                           # Add button
            form = RRForm(request.POST)
            if form.is_valid():
                rrlist = dom.rrs.splitlines()
                rrlist.append(form.cleaned_data.get('dnsrecord'))
                dom.rrs = "\n".join(rrlist)
                dom.updated = timezone.now()
                dom.save()
                return editview(request, domainname, postok=False)

        # otherwise fall through to edit again
    else:
        rrname = request.POST['rrname']
        form = RRForm(rrname=rrname)

    return render(request, 'editapp/recordadd.html',
        {
            'form': form,
            'domain': domainname,
            'bpnav': bpnav(request, 'edit')
        })



def dologout(request):
    """
    log out, return to main screen
    """
    logout(request)
    return redirect("/login/?next=/edit/")

@login_required
def testview(request):
    """
    test page
    """

    kvetch = None
    if request.method == 'POST':
        form = RRForm(request.POST)
        if form.is_valid():
            form = "The record is: "+form.cleaned_data.get('dnsrecord')
        else:
            kvetch = "not valid "+repr(form.errors)
    else:
        form = RRForm("PARP MX 1 this.that")


    return render(request, 'editapp/test.html',
        {
            'kvetch': kvetch,
            'form': form,
            'bpnav': bpnav(request, 'test')
        })

# boilerplate navigation toolbar at the top of each page
def bpnav(request, here):
    """
    return HTML for boilerplate navigation toolbar
    here is current page
    """
    def bp(page, desc):
        if here in page:
            return "<li><a href=\"{}\" class=active>{}</a></li>\n".format(page,desc)
        else:
            return "<li><a href=\"{}\">{}</a></li>\n".format(page,desc)

    bo = "<ul id=tabnav>\n"
    bo += bp("/edit","Home")
    bo += bp("/edit/create","Create a domain")
#    bo += bp("/edit/test","Test something")
    bo += bp("/admin","Admin")
    bo += bp("/logout?next=/edit", "Logout")
    bo += "</ul>\n<p align=right>Logged in as " + request.user.username
    if request.user.has_perm('dnsedit.see_all'):
        bo += " (all)"
    bo += "</p>"
    return bo
