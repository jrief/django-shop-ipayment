#!/bin/bash

args=("$@")
num_args=${#args[@]}
index=0

suite='project'
coverage=false
documentation=false
ci=false
liveserver="localhost:8080"

while [ "$index" -lt "$num_args" ]
do
	case "${args[$index]}" in
		"--with-docs")
			documentation=true
			;;
		"--with-coverage")
			coverage=true
			;;
		"--ci")
			ci=true
			;;
		"--liveserver")
			let "index=$index+1"
			if [ $index -eq "$num_args" ]; then
				exec >&2; echo "error: --liveserver requires an argument"; exit 1
			fi
			liveserver=${args[$index]}
			if ! [[ "$liveserver" =~ ^[0-9A-Za-z\.-]+:[0-9]+$ ]] ; then
				exec >&2; echo "usage: --liveserver <hostname>:<port>"; exit 1
			fi
			;;
		*)
			suite="shop.${args[$index]}"
	esac
let "index = $index + 1"
done
if [ $ci == true ]; then
	pushd .
	cd tests/testapp
	coverage run manage.py test --liveserver=$liveserver $suite
	coverage xml
	popd

elif [ $coverage == true ]; then
	pushd .
	cd tests/testapp
	coverage run manage.py test --liveserver=$liveserver $suite
	coverage html
	#x-www-browser htmlcov/index.html
	popd
else

	# the default case...
	pushd .
	cd tests/testapp
	python manage.py test --liveserver=$liveserver $suite
	popd
fi

if [ $documentation == true ]; then
	pushd .
	cd docs/
	make html
	x-www-browser _build/html/index.html
	popd
fi

