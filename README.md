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