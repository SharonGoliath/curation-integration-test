#!/bin/bash

echo "ingest_modify_local"
cd ${I}/ingest_modify_local || exit $?
for f_name in C080121_0339_SCI.fits C180108_0002_SCI.fits.gz
do
    cadc-data get --cert $HOME/.ssl/cadcproxy.pem OMM ${f_name} || exit $?
done

echo "retries"
cd ${I}/retries || exit $?
for f_name in C120402_domeflat_J_CALRED.fits.gz C180108_0002_SCI.fits
do
    cadc-data get --cert $HOME/.ssl/cadcproxy.pem OMM ${f_name} || exit $?
done

echo "scrape and scrape_modify"
cd ${I}/scrape || exit $?
for f_name in C170324_0054_SCI.fits.gz
do
    cadc-data get --cert $HOME/.ssl/cadcproxy.pem OMM ${f_name} || exit $?
    cp ${I}/scrape/${f_name} ${I}/scrape_modify || exit $?
done

echo "store_ingest_modify"
cd ${I}/store_ingest_modify || exit $?
for f_name in C180616_0135_SCI.fits
do
    cadc-data get --cert $HOME/.ssl/cadcproxy.pem OMM ${f_name} || exit $?
done
date
exit 0
