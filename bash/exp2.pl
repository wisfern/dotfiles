#!/usr/bin/perl

use Expect;
my $obj = shift;

if ($obj eq "dz") {

        $ept = Expect->spawn( "ssh -p 10167 -l ngboss 172.16.1.20" ) or die $!;
        $ept->send("Cbe\@2015!\n") if $ept->expect(10, re=>'Password');
        $ept->send("ssh -l cjzh 10.252.152.42 \n") if $ept->expect(10, re=>'CBE');
#       $ept->send("JfQy#2015\n") if $ept->expect(10, re=>'password');
        $ept->interact();  #    把控制权转交给用户
 
        exit;
} elsif ($obj eq "dzx86") {
        $ept = Expect->spawn( "ssh -p 10167 -l ngboss 172.16.1.20" ) or die $!;
        $ept->send("Cbe\@2015!\n") if $ept->expect(10, re=>'Password');
        $ept->send("ssh -l yxcs 10.252.130.136 \n") if $ept->expect(10, re=>'CBE');
        $ept->send("Gmcc#2016\n") if $ept->expect(10, re=>'Password');
        $ept->interact();  #    把控制权转交给用户
 
        exit;

}
