#!/bin/bash
curl -L --post302 --data "confirmed=Oui,%20je%20veux%20la%20supprimer&verif=$2" $1$2 > /dev/null 2>&1
echo "$1$2 deleted by $3"
