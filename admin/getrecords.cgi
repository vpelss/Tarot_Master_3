#!/usr/bin/perl

#use JSON;
require "JSON.pm";

$json = JSON->new->allow_nonref;
$json->pretty([$enable]);

print "Content-type: text/html\n\n";

my %in = &parse_form();
#$in{databasefile} = "../../../tarotmaster/databases/small.cgi";
my %deck;
my @database;

#GET our tarot deck
open (DATABASE, "$in{databasefile}") || die("no database file at $in{databasefile}");
@db= <DATABASE>;
close DATABASE;
@db = grep(/\w/, @db); #remove blank lines in db!!!

#build a hash %db_def of the field names and positions eg: #field_name => ['position']
$db[0] =~ s/\n//g;
@field_names_array  = split(/\|/,$db[0]); #this is a list of all database field names from first line of database
shift @db; #remove fields name from deck database
$field_count = @field_names_array;
foreach $field (0..($field_count - 1)) #create field hash %db_def of the field names eg: #field_name => ['position']
         {
         $fn = $field_names_array[$field];
         $fn =~ s/\n//g;
         $fn =~ s/\r//g;
         $db_def{$fn} = $field;
         }

$recordIndex = 0;
foreach $item (@db) #for each line in db
         {
         $item =~ s/\n//g;
         @record  = split(/\|/,$item);
         $fieldIndex = 0;
         foreach $fieldData (@record)
                  {
                  $record{$field_names_array[$fieldIndex]} = $fieldData;
                  $fieldIndex++;
                  }
         #$database{$recordIndex} = {%record};
         push @database , {%record};
         #$database[$recordIndex] = {%record};
         #$database[$recordIndex] = 8;
         $recordIndex++;
         }

$json_text = $json->encode( [@database] );

print $json_text;
exit;


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
                &cgierr ("This script must be called from the Web\n using either GET or POST requests\n\n");
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
}