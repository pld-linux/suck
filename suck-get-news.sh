#!/bin/sh

# $Revision$

#BEFORE USING - check to ensure all the paths defined below are correct!!

#NOTE: this script probably needs to be run by root.  Most systems will
# not let a normal user run ctlinnd 

SPOOLDIR=/var/spool/news	# base directory for articles to be rposted
NEWSDIR=/usr			# base directory for news binaries 

CTLINND=${NEWSDIR}/bin/ctlinnd	# location of binary
SHLOCK=${NEWSDIR}/bin/shlock	# location of binary

OUTFILE=/tmp/tmp$$			# used by rpost as article after it is filtered
NEWSGROUP=news				# which group owns the file in
					# outgoing, typically either news or 
					# uucp.
TESTHOST=testhost
SUCK=suck

# for INN 2.x with Storage API use:
RPOST=rpost				# rpost command
# for INN <2.3 without storage API use:
#SCRIPT=${BASEDIR}/put.news		# my filter for rpost
#RPOST="rpost -p ${SPOOLDIR}"		# rpost command

for CONFIG_FILE in /etc/news/suck/*; do

echo "************************************************************"
echo "Processing $CONFIG_FILE:"
echo "************************************************************"

REMOTE_HOST=
SITE=			# name of site from newsfeeds file
LOCAL_HOST=

VIA_SSH=no
VIA_HOST=
VIA_PORT=
VIA_USER=	
USE_MODEREADER=
BASEDIR=/tmp

# read config from file:

. $CONFIG_FILE

LOCKFILE=${BASEDIR}/getnews.lock	# lock file to prevent multiple instances of script
SCRIPT=${BASEDIR}/put.news.sm		# my filter for rpost
TMPDIR=${BASEDIR}		# location for suck.* files
MSGDIR=${BASEDIR}/Msgs		# where to put MultiFile messages when 
				# getting them

OUTGOING=${SPOOLDIR}/outgoing/${SITE}	# location of the list of articles 
					# to upload
OUTGOINGNEW=${OUTGOING}.new		# file to contain the list temporarily
OUTGOINGFAIL=${OUTGOINGNEW}.fail	# file with failed xfers

# if we are already running, abort 
trap 'rm -f ${LOCKFILE} ; echo "Aborting" ; exit 1' 1 2 3 15
${SHLOCK} -p $$ -f ${LOCKFILE}
if [ $? -ne 0 ]; then
	echo "Already running, can't run two at one time"
	exit
fi


if [ ${VIA_SSH} == "yes" ]; then
	
	su $VIA_USER -c "ssh -f -C -L $VIA_PORT:news.mimuw.edu.pl:119 \
	-l $VIA_USER $VIA_HOST sleep 120"

fi

# is the local host up and running so we can post messages we download?
${TESTHOST} ${LOCAL_HOST} -s ${USE_MODEREADER}
LOCAL_RESULT=0

# is the remote host up and running so we can download messages?
if [ ${VIA_SSH} == "yes" ]; then
	${TESTHOST} localhost -N $VIA_PORT -s ${USE_MODEREADER}
	REMOTE_RESULT=$?
else
	${TESTHOST} ${REMOTE_HOST} -s
	REMOTE_RESULT=$?
fi	

if [ ${REMOTE_RESULT} -eq 0 -a ${LOCAL_RESULT} -eq 0 ]; then
	{
		# download messages
		if [ ${VIA_SSH} == "yes" ]; then
			${SUCK} localhost -N $VIA_PORT -c -A -bp -hl ${LOCAL_HOST} -dt ${TMPDIR} -dm ${MSGDIR} -dd ${BASEDIR} ${USE_MODEREADER} -i 500
		SUCK_STATUS=$?
		else
			${SUCK} ${REMOTE_HOST} -c -A -bp -hl ${LOCAL_HOST} -dt ${TMPDIR} -dm ${MSGDIR} -dd ${BASEDIR}
		SUCK_STATUS=$?
		fi

		if [ ${SUCK_STATUS} -eq 0 ]; then
			echo "Downloaded Articles"
		elif [ ${SUCK_STATUS} -eq 1 ]; then
			echo "No articles to download"
		elif [ ${SUCK_STATUS} -eq 2 ]; then
			echo "Unexpected answer from remote server to an issued command"
		elif [ ${SUCK_STATUS} -eq 4 ]; then
			echo "Can't do NNTP authorization"
		elif [ ${SUCK_STATUS} -eq -1 ]; then
			echo "General failure"
		fi
	} &

	{
		# upload messages
		if [ -s ${OUTGOING}  -o -s ${OUTGOINGNEW} ]; then

			if [ ${VIA_SSH} == "yes" ]; then
				${TESTHOST} localhost -N $VIA_PORT -s
				RESULT=$?
			else
				  ${TESTHOST} ${REMOTE_HOST} -s
				RESULT=$?
			fi			  

			if [ $RESULT -ne 0 ]; then
				echo "Remote posting host not responding"
			else
	# this is needed by INND so that the outgoing file will be
	# properly flushed and we have a new blank file to work with
	# when we are done
	# First mv the current one to a new file name
	# Since innd already has the file open, it doesn't care 
	# about the rename.
	# The flush will ensure that all messages to be posted have
	# been written out, close off the old one (already renamed)
	# and create a new one.

	# if the outgoingnew already exists, it means we aborted last time
	# so don't try to do it again
				if [ ! -s ${OUTGOINGNEW} ]; then
					mv ${OUTGOING} ${OUTGOINGNEW}
					${CTLINND} flush ${SITE}
				fi

	# outgoing messages to post
				if [ ${VIA_SSH} == "yes" ]; then
					${RPOST} localhost -N ${VIA_PORT} ${USE_MODEREADER} -d -b ${OUTGOINGNEW} -f \$\$o=${OUTFILE} ${SCRIPT} \$\$i ${OUTFILE}
				ERRLEV=$?
				else			
					${RPOST} ${REMOTE_HOST} -d -b ${OUTGOINGNEW} -f \$\$o=${OUTFILE} ${SCRIPT} \$\$i ${OUTFILE}
				ERRLEV=$?
				fi				

				if [ ${ERRLEV} -eq 0 ]; then
					echo "Remotely posted articles"
					rm ${OUTFILE}
				elif [ ${ERRLEV} -eq 1 ]; then
					echo "Error posting a message"
				elif [ ${ERRLEV} -eq 2 ]; then
					echo "Unable to do NNTP authorization with remote server"
				elif [ ${ERRLEV} -eq 3 ]; then
					echo "Unexpected answer from remote server to a command while doing NNTP authorization"
				elif [ ${ERRLEV} -eq -1 ]; then
					echo "Fatal error"
				fi

				if [ -f ${OUTGOINGFAIL} ]; then
					mv ${OUTGOINGFAIL} ${OUTGOINGNEW}	# so we can re do it
					chown news.${NEWSGROUP} ${OUTGOINGNEW}
					chmod 664 ${OUTGOINGNEW}
				fi
			fi
		fi	
	} &

	wait


fi

rm -f ${LOCKFILE}

echo "File $CONFIG_FILE processed"

done
	echo "You can hang up the modem now"
