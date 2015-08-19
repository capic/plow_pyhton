#!/bin/bash
PATH=/opt/someApp/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

entree=.
destination=/mnt/HD/HD_a2/downloads/
nbTelechargements=-1
xTermExiste=""
nomScreen=""

while getopts ":u:d:e:n:s:" option
do
	case ${option} in
		e)
			entree=${OPTARG}
			echo "Repertoire d'entree ${entree}"
			;;
		d)
			destination=${OPTARG}
			echo "Repertoire de destination ${destination}"
			;;
		n)	nbTelechargements=${OPTARG}
			echo "Nombre telechargements simultannees ${nbTelechargements}"
			;;
		s)	nomScreen=${OPTARG}
			echo "Nom du screen : ${nomScreen}"
			;;
		u)
			opt_u="true"
			;;
		:)
			echo "nom du repertoire de destination absent"
			;;
		\?)
			echo " option invalide"
			exit 1
			;;
	esac
done

#on verifie si screen est installe
#which screen > xTermExiste

#if ${xTermExiste}

liste=$(ls ${entree} | egrep "*.txt")
destination_temp=${destination}temp_plowdown/


	cd /usr/local/plowshare4
	git stash
	git pull
	make install
	cd /root/.config/plowshare/modules.d/legacy.git
	git stash
	plowmod --update
	cp -r /root/.config /



repLog=${destination_temp}log/

echo "wipe screen"
screen -wipe

if [ -f ${entree} ]; then
	command="/usr/bin/plowdown -r 10 -x -m --9kweu=I1QOR00P692PN4Q4669U --temp-rename --temp-directory ${destination_temp} -o ${destination} ${entree}"
	echo ${command}
	screen -dmS ${nomScreen} -m '/mnt/HD/HD_a2/screen.sh -e ${entree} -d ${destination}'
else
	echo ${liste}
	for fich in ${liste}
	do

		#si on a un repertoire on liste tous les liens dans un fichier texte
		#if [[${fich} =~ ""]]; then
		#	plowlist
		#fi

		# traitement de liens a inserer en bdd
		nomScreen="treat-${fich}"
		command="python /var/www/main/download_basic.py start_file_treatment ${entree}/${fich}"
		echo ${command}
		screen -list | grep ${nomScreen} > /dev/null
		if [ $? -eq 1  ]; then
			screen -dmS ${nomScreen} -m ${command}
		fi

		nomScreen="down-${fich}"
		screen -list | grep ${nomScreen} > /dev/null
		if [ $? -eq 1  ]; then
			echo "**** Nom du screen : ${nomScreen}"
			# command="/usr/bin/plowdown -r10 -x -m --9kweu=I1QOR00P692PN4Q4669U --temp-rename --temp-directory ${destination_temp} -o ${destination} ${entree}/${fich}"
			command="python /var/www/main/download_basic.py start_multi_downloads ${entree}/${fich}"
			echo ${command}
			screen -dmS ${nomScreen} -m ${command}
		else
			echo "---- screen ${nomScreen} existant"
		fi
	done
fi
#echo "nombre de fichier txt : ${compteur}"
#while [ ${compteur} -le ${nbFichiers} ];
#do
	#for fich in `seq 1 ${nbTelechargement}`
	#do
		#/usr/bin/plowdown -x -m --temp-rename --temp-directory ${destination_temp} -o ${destination} ${entree}/${liste[fich]}
	#	command="/usr/bin/plowdown -x -m --temp-rename --temp-directory ${destination_temp} -o ${destination} ${entree}/${liste[fich]}"
	#	echo ${command}
	#	xterm -e "${command}; $SHELL" &

		#echo ${retour};
	#done

#	compteur=$((${compteur}+1))
#	echo ${compteur}
#done

