#!/usr/bin/perl

use HTML::Entities;

eval {
      require "../chat_vars.cgi";  #load up common variables and routines. // &cgierr
      };
warn $@ if $@;

print "Content-type: text/html\n\n";
print "Content-Length: ", length(''), "\r\n\r\n"; #closes connection immediately for IE limited connection settings...

%in = &parse_form;

$sessioncode = HTML::Entities::encode($in{sessioncode}); #escape text to avoid code being run. Cross-site Scripting Attacks
$sessioncode =~ s/ //g; # remove spaces so we can't create directories where we are not suposed to
#$sessioncode =~ s/\W//g; # remove any non word char

if ($sessioncode eq "") {exit} #do not allow writing in the root /tarotmaster2/output/

$chatdirectory = "$chattextpath/$sessioncode";
$chatfile = "../$chatdirectory/index.txt";

if ($in{'table'} ne '')
    {
    $temp2 = $in{'table'};
    #$temp2 = HTML::Entities::encode($in{'table'}); #escape text to avoid code being run. Cross-site Scripting Attacks

    #write archice file
    open (DATA, ">$chatfile") or die("Could not create file $chatfile");
    flock(DATA , LOCK_EX);
    print DATA "$temp2";
    flock(DATA , LOCK_UN);
    close (DATA);
    }


sub unix_to_date {
# --------------------------------------------------------
# This routine must take a unix time and return your date format
# A much simpler routine, just make sure your format isn't so complex that
# you can't get it back into unix time.
#
    my $time   = shift;
    my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $tz) = localtime $time;
    my @months = qw!Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec!;
    $year      = $year + 1900;
    return "$day-$months[$mon]-$year $hour:$min:$sec";
}

sub parse_form {
# --------------------------------------------------------
# Parses the form input and returns a hash with all the name
# value pairs. Removes SSI and any field with "---" as a value
# (as this denotes an empty SELECT field.

        my (@pairs, %in);
        my ($buffer, $pair, $name, $value);

        if ($ENV{'REQUEST_METHOD'} eq 'GET') {
                @pairs = split(/&/, $ENV{'QUERY_STRING'});
        }
        elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
                read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
                 @pairs = split(/&/, $buffer);
        }
        else {
                &cgierr ("This script must be called from the Web\nusing either GET or POST requests\n\n");
        }
        PAIR: foreach $pair (@pairs) {
                ($name, $value) = split(/=/, $pair);

                $name =~ tr/+/ /;
                $name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

                $value =~ tr/+/ /;
                $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

                $value =~ s/<!--(.|\n)*-->//g;                          # Remove SSI.
                if ($value eq "---") { next PAIR; }                  # This is used as a default choice for select lists and is ignored.
                (exists $in{$name}) ?
                        ($in{$name} .= "~~$value") :              # If we have multiple select, then we tack on
                        ($in{$name}  = $value);                                  # using the ~~ as a seperator.
        }
        return %in;
};