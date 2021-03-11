#!/bin/bash

# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

# Test validate command
VALIDATE='python ../src/validate.py'

# No arguments
echo ""
echo "No arguments"
$VALIDATE

# Bad ontology directory
echo ""
echo "Bad ontology directory"
$VALIDATE testdata

# Bad ontology serialized file
echo ""
echo "Bad ontology serialized file"
$VALIDATE testdata/ontology/README

# Good ontology, no data
echo ""
echo "Good ontology, no data"
$VALIDATE testdata/ontology/tiny_ontology

# Good ontology, bad data
echo ""
echo "Good ontology, bad data"
$VALIDATE testdata/ontology/tiny_ontology.pkl testdata/ontology

# Good ontology, bad data
echo ""
echo "Good ontology, bad data"
$VALIDATE testdata/ontology/tiny_ontology.pkl testdata/ontology/tiny_ontology/README

# Good ontology, bad data
echo ""
echo "Good ontology, bad data"
$VALIDATE testdata/ontology/tiny_ontology.pkl testdata/ontology/tiny_ontology.pkl

# Good ontology, good data
echo ""
echo "Good ontology, good data"
$VALIDATE testdata/ontology/tiny_ontology.pkl testdata/casedata/tiny_data.json

# Good ontology, multiple good and bad data
echo ""
echo "Good ontology, multiple good and bad data"
$VALIDATE testdata/ontology/tiny_ontology.pkl testdata/ontology testdata/casedata/tiny_data.json

# Good ontology, multiple good data
echo ""
echo "Good ontology, multiple good data"
$VALIDATE testdata/ontology/full_ontology.pkl testdata/casedata/tiny_data.json testdata/casedata/tiny_data.pkl
