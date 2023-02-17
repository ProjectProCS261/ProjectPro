#!/bin/bash
app="projectpro"
docker build -t ${app} .
docker run -d -p 56733:80 \
  --name=${app} \
  -v $pwd:/app ${app}
