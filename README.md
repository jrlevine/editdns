# DNS editing sample app

This is a simple django app that uses the extlang library to edit DNS
zones.  Install it the usual way, make migrations for editapp, migrate
to create the database, then create users in the django admin.  There
is one extra permission flag:

  editapp | domain | Can see all users' domains

Users only can see their own domains if the flag is not set.

## Editing zones

The web page tabs are intended to be self-explanatory.  The Create tab
creates a zone containing only a comment line.  Edit lets you edit or
add records using the extlang syntax prompting.  On the edit page, the
Block edit button lets you edit the zone as a block of test.  The
edited text is syntax checked before being stored.

## Exporting zones

To export the zones to files, use 

  python3 manage.py export [--list listfile ] [--all zonedir] [--updated zonedir]

It can list the zones into listfile, or store zones into zonedir, with
each zone in a file with the name of the zone.  The --all flag stores
all zones, --updated only the ones changed since they were exported.

If there is a pseudo-zone called HEAD its contents are prefixed to
each zone.  If HEAD includes an SOA record, the sequence number is
replaced with the current Unix timestamp, so updated zone automatically
get updated sequence numbers.

John Levine, john.levine@standcore.com, June 2017

## License

Copyright 2017, ICANN and Standcore LLC.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
