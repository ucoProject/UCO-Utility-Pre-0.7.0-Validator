#!/bin/bash

# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

# Test describe command
DESCRIBE='python ../src/describe.py'

# No arguments
echo ""
echo "No arguments"
$DESCRIBE

# Serialized ontology
echo ""
echo "Serialized ontology"
$DESCRIBE testdata/serializer/serialized_ontology.pkl

# Serialized jsonld
echo ""
echo "Serialized jsonld"
$DESCRIBE testdata/casedata/Oresteia.pkl

# Bad file
echo ""
echo "Bad file"
$DESCRIBE testdata/ontology/tiny_ontology/README

# Directory
echo ""
echo "Directory"
$DESCRIBE testdata
