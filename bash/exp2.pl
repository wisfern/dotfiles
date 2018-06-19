#!/usr/bin/perl

use Expect;
my ($obj, $arg1, $arg2) = @ARGV;
if ($obj eq "dz") {
    $ept = Expect->spawn( "ssh -p 10167 -l ngboss 172.16.1.20" ) or die $!;
    $ept->send("Cbe\@2015!\n") if $ept->expect(10, re=>'Password');
    $ept->send("ssh -l cjzh 10.252.152.42 \n") if $ept->expect(10, re=>'CBE');
#   $ept->send("JfQy#2015\n") if $ept->expect(10, re=>'password');
    $ept->interact();  #    把控制权转交给用户

    exit;
} elsif ($obj eq "dzx86") {
    $ept = Expect->spawn( "ssh -p 10167 -l ngboss 172.16.1.20" ) or die $!;
    $ept->send("Cbe\@2015!\n") if $ept->expect(10, re=>'Password');
    $ept->send("ssh -l yxcs 10.252.130.136 \n") if $ept->expect(10, re=>'CBE');
    $ept->send("Gmcc#2016\n") if $ept->expect(10, re=>'Password');
    $ept->interact();  #    把控制权转交给用户

    exit;

} elsif ($obj eq "srjh") {
	$ept = Expect->spawn( "ssh -p 10137 -l xiezf 172.16.1.20" ) or die $!;
    #$ept->send("402890\@xf\n") if $ept->expect(5, '-re', 'assword');
    $ept->send("ssh3\n") if $ept->expect(5, '-re', 'BIHZWG02');
    #$ept->send("ssh ng3_kf\@192.252.105.3\n") if $ept->expect(10, re=>'SRJH-FS-DB01');
	$ept->interact();      #    把控制权转交给用户

	exit;
} elsif ($obj eq "send2srjh") {
	$filename = (split /\//, $arg1)[-1];

	#$ept = Expect->spawn( "scp -P 10142 $arg1 bd_srjh\@172.16.1.20:~/$filename; echo ____END____" ) or die $!;
	$ept = Expect->spawn( "scp -P 10142 $arg1 bd_srjh\@172.16.1.20:~/$filename" ) or die $!;
	$ept->send("gmcc1234\n") if $ept->expect(5, '-re', 'password');

	$ept1 = Expect->spawn("ssh -p 10142 -l bd_srjh 172.16.1.20" ) if $ept->expect(360, re=>'100%');
	$ept1->send("gmcc1234\n") if $ept1->expect(10, re=>'password');
	$ept1->send("scp $filename ng3_kf\@192.252.105.3:~/$filename \n") if $ept1->expect(360, re=>'SRJH-FS-DB01');
	if ($ept1->expect(30, re=>'100%')) {
		sleep 2;
		$ept1->send("rm -rf $filename\n");
		$ept1->send("ssh ng3_kf\@192.252.105.3 \n");
	}
	#$ept1->send("scp $filename ng3_kf\@192.252.0.158:~/$filename \n") if $ept1->expect(5, re=>'SRJH-DB-01');
	#$ept1->send("rm -rf $filename \n") if $ept1->expect(30, re=>'100%');
	#$ept1->hard_close() if $ept1->expect(5, re=>'ng3_kf');
	print "\ndone!\n";
	exit;
}
