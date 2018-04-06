# DNS extension language display and parse routines django form
# interface
# python3 only
# version 1.0

# exception classes
from dnsextlang import ExtSyntax, ExtKeytype, ExtBadField, ExtUnimp, fieldclasses

import dns.tokenizer
import dns.rdataclass
import dns.exception

import re

# field types
from dnsextlang import ExtFieldS,ExtFieldN, ExtFieldX, ExtFieldA, ExtFieldAA, ExtFieldAAAA, \
    ExtFieldB32, ExtFieldB64, ExtFieldR, ExtFieldT, ExtFieldI1, ExtFieldI2, ExtFieldI4, \
    ExtFieldX6, ExtFieldX8, ExtFieldZ

# manage rrtypes and collections of rrtypes
from dnsextlang import Extlang, Extlangrr

# parse and deparse records and lists of records
from dnsextlang import Extrec, ExtComment, ExtrecMulti, ExtrecList, fieldclasses

from django import forms
from django.forms.widgets import Textarea, HiddenInput
from django.core.exceptions import ValidationError
from django.http.request import QueryDict

# extlang instance used by all the parsing stuff
extxl = Extlang(domain='services.net')

def validate_rrs(rrs):
    """
    see if a chunk of code is a valid list of rrs
    """
    l = ExtrecList(extxl, string=rrs)
    if not l.is_valid():
        raise ValidationError(l.err_str())

class RRField(forms.CharField):
    """
    a validated text field of RRs
    """
    def __init__(self, *args, **kwargs):
        super(RRField, self).__init__(widget=Textarea,
            validators=[validate_rrs], help_text = "DNS records for a zone",
            *args, **kwargs)

################
# create a form on the fly for the fields in an RR

# formatting functions to turn an RR field into a django Field
def fieldfuni(field):
    """
    integer
    """
    return forms.IntegerField(label=field.name, initial=field, help_text="Number",
        min_value=0, max_value=(1 << (8*field.fieldlen)-1))

def fieldfuns(field):
    """
    strings
    """
    return forms.CharField(label=field.name, initial=field,
        help_text="Text strings" if field.is_multi() else "Text string")

def fieldfunn(field):
    """
    domain names
    """
    return forms.CharField(label=field.name, initial=field, help_text="Domain name")

def fieldfuna(field):
    """
    ipv4 address
    """
    return forms.GenericIPAddressField(label=field.name, initial=field,
        protocol="IPv4", help_text="IPv4 address")

def fieldfunaa(field):
    """
    64 bit number like half a v6 address
    """
    return forms.CharField(label=field.name, initial=field,
        help_text="64 bit locator/ID")

def fieldfunaaaa(field):
    """
    ipv6 address
    """
    return forms.GenericIPAddressField(label=field.name,
        initial=field, protocol="IPv6", help_text="IPv6 address")

def fieldfunr(field):
    """
    rrname(s)
    """
    return forms.CharField(label=field.name, initial=field, help_text="RRNAME" if field.is_multi() else "RRNAME")

def validate_xx(hexstr):
    """
    validate multiple hex strings
    """
    return validate_x(hexstr, multi=True)

def validate_x(hexstr, multi=False):
    """
    validate one or more hex strings
    """
    # allow spaces if multi
    r = re.match(r'^[0-9a-f ]+$' if multi else r'^[0-9a-f]+$', hexstr, flags=re.a|re.i) #
    if not r:
        raise ValidationError("Hex string{0} needed".format("s" if multi else ""))

def fieldfunx(field):
    """
    hex string(s)
    """
    if field.is_multi():
        validator = [validate_xx]
    else:
        validator = [validate_x]
    return forms.CharField(label=field.name, initial=field, help_text="Hex strings" if field.is_multi() else "Hex value",
        validator=validator)

def validate_n(name):
    """
    validate a domain name
    """
    # pattern for a DNS name, with \nnn octal escapes
    # should use the one in extfieldN
    _namepattern = re.compile(r"""[*0-9a-z_] ((\\[0-7]{3}|[-0-9a-z_])*(\\[0-7]{3}|[0-9a-z_])?)
        (\.(\\[0-7]{3}|[0-9a-z_])((\\[0-7]{3}|[-0-9a-z_])*(\\[0-7]{3}|[0-9a-z_])?))* \.?|\.""",
        re.I|re.X)
    r = _namepattern.fullmatch(name) # close enough
    if not r:
        raise ValidationError("Domain name needed")

def fieldfunxn(field):
    """
    EUI 48 and 64
    """
    return forms.CharField(label=field.name, initial=field, help_text="EUI{0} identifier".format(8*field.fieldlen))

def fieldfunb32(field):
    """
    base 32
    """
    return forms.CharField(label=field.name, initial=field, help_text="Base32 value")

def fieldfunb64(field):
    """
    base 64
    """
    return forms.CharField(label=field.name, initial=field, help_text="Base64 text")

def fieldfunt(field):
    """
    timestamp
    xxx need to decode timestamps and YYYYMMDDHHmmSS
    """
    return forms.DateTimeField(label=field.name, initial=field, help_text="Time stamp")

def fieldfunz(field):
    """
    other unimplemented
    """
    return None

fieldfns = {
    'I1': fieldfuni, 'I2': fieldfuni, 'I4': fieldfuni,
    'S': fieldfuns, 'N': fieldfunn,
    'A': fieldfuna, 'AA': fieldfunaa, 'AAAA': fieldfunaaaa,
    'R': fieldfunr, 'X': fieldfunx, 'X6': fieldfunxn, 'X8': fieldfunxn,
    'B32': fieldfunb32, 'B64': fieldfunb64, 'T': fieldfunt, 'Z': fieldfunz
    }

class RRForm(forms.Form):
    """
    form to edit a single RR using the fields from dnsextlang
    can be created from a text RR, or a dict of edited values
    or rrname="XXX" for new empty RR
    """

    # fields common to all rr forms
    name = forms.CharField(required=False, help_text="Name of this record or blank",
        validators=[validate_n])
    ttl = forms.IntegerField(label="TTL", required=False, help_text="Time to live",
        min_value=0, max_value=65535)

    rrname0 = forms.CharField(widget=HiddenInput) # passed back so it knows what to reconstruct

    def __init__(self, *args, **kwargs):
        if 'rrname' in kwargs:          # new empty record
            rrname = kwargs['rrname']
            del kwargs['rrname']
            super(RRForm, self).__init__(initial = { 'rrname0': rrname }, **kwargs)

            # make an empty RR of the right type
            self.rec = Extrec(extxl, rrtype=rrname)

            # visible field if form will be displayed
            # added here due to binding problem noted below
            self.fields['rrname'] = forms.CharField(label="rrname",
                initial=rrname, disabled=True)

            # add fields for rrtype fields
            for n, f in enumerate(self.rec.fields, start=0):
                self.fields['rr{0}'.format(n)] = fieldfns[f.fieldtype](f)
            return
        
        if type(args[0]) is str:        # parse up an string RR into an unbound form
            rr = args[0]
            self.rec = Extrec(extxl, rr)
        
            # populate common fields with values from the rr
            super(RRForm, self).__init__(initial = { 'name': self.rec.name, 'ttl': self.rec.ttl,
                    'rrname0': self.rec.rr.rrname }, **kwargs)

            # visible field if form will be displayed
            # added here due to binding problem noted below
            self.fields['rrname'] = forms.CharField(label="rrname",
                initial=self.rec.rr.rrname, disabled=True)

            # add fields for rrtype fields
            for n, f in enumerate(self.rec.fields, start=0):
                self.fields['rr{0}'.format(n)] = fieldfns[f.fieldtype](f)
            return
        
        if type(args[0]) in (dict, QueryDict):  # create bound form from dict data
            qd = args[0]
            rrname = qd['rrname0']
            super(RRForm, self).__init__(data=qd)
            
            self.rec = Extrec(extxl, noinit=True)  # empty extrec for us to fill
            self.rec.rr = extxl[rrname]  # set the rrtype
            self.rec.fields = self.rec.rr.getfields()
            self.rec.lineno = None
            
            # visible field in case form will be displayed
            # have to add it here because __init__ doesn't set
            # disabled fields
            self.fields['rrname'] = forms.CharField(label="rrname",
                initial=rrname, disabled=True) # display only for the user

            # optional ttl
            ttl = qd.get("ttl")
            if type(ttl) is str and ttl.isdecimal():
                self.rec.ttl = int(ttl)
            else:
                self.rec.ttl = None

            # optional name
            name = qd.get("name")
            if name:
                try:
                    tok = dns.tokenizer.Token(dns.tokenizer.IDENTIFIER, name, ('\\' in name))
                except dns.exception.DNSException as e:
                    raise ValidationError("Invalid name field")

                self.rec.name = fieldclasses["N"]("name", None, None, value=tok)
            else:
                self.rec.name = None

            # set up all the fields that have data
            for n, f in enumerate(self.rec.fields, start=0):
                fval = qd.get('rr{0}'.format(n))
                if fval:
                    # initialize the extlang field
                    tokens = dns.tokenizer.Tokenizer(fval, filename='<field {0}>'.format(f.name))
                    if f.multi:
                        # get as many tokens as there are
                        toks = []
                        while True:
                            try:
                                tok = tokens.get()
                            except dns.exception.UnexpectedEnd as e:
                                raise ValidationError("Truncated %(name)", params={'name': f.name})
                            
                            if tok.is_eol_or_eof():
                                break
                            toks.append(tok)
                        f.parse(toks)
                    else:
                        # try to get one token
                        try:
                            tok = tokens.get()
                        except dns.exception.DNSException as e:
                            raise ValidationError("Invalid %(name)", params={'name': f.name})
                        if not tok.is_eol_or_eof():
                            f.parse(tok)
                        try:
                            tok = tokens.get()
                        except dns.exception.DNSException as e:
                            raise ExtSyntax(e.msg)

                    # check for junk and end of field
                    if not tok.is_eol_or_eof():
                        f.valid = False
                        f.errstr = "junk at end of field"
                        f.value = fval  # so user can try again

                # set up the form field now that it has thed data if
                # any
                self.fields['rr{0}'.format(n)] = fieldfns[f.fieldtype](f)

            # set whether the extrec is valid, can be tested in clean() below
            self.rec.valid = all((f.is_valid() for f in self.rec.fields))
            if self.rec.valid and self.rec.name:
                self.rec.valid = self.rec.name.is_valid()
            return
        # not a string or a querydict, I give up
        raise ValidationError("Mystery RRForm data")
                
    def clean(self):
        """
        splice everything into a text RR if possible
        """
        if not self.rec.is_valid():
            raise ValidationError(self.rec.err_str())

        self.cleaned_data['dnsrecord'] = str(self.rec)
        return self.cleaned_data

def validate_comment(comment):
    """
    make sure it's a comment
    """
    if comment.strip()[0] != ';':
        raise ValidationError("Not a comment")

class CommentForm(forms.Form):
    """
    form to edit a single comment line
    """
    rrname0 = forms.CharField(widget=HiddenInput, initial="COMMENT") # passed back so it knows what to reconstruct
    comment = forms.CharField(label='Comment', max_length=100, validators=[validate_comment])
