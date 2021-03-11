#!/bin/bash

# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

# Test serialize command
SERIALIZE='python ../src/serialize.py'

# No arguments
echo ""
echo "No arguments"
$SERIALIZE

# Good ontology directory
echo ""
echo "Good ontology directory"
$SERIALIZE -c comments -o foo.pkl testdata/ontology/tiny_ontology

# Bad ontology directory
echo ""
echo "Bad ontology directory"
$SERIALIZE -c comments -o foo.pkl testdata

# Good json-ld file
echo ""
echo "Good json-ld file"
$SERIALIZE -c comments -o foo.pkl testdata/casedata/tiny_data.json

# Bad json-ld file
echo ""
echo "Bad json-ld file"
$SERIALIZE -c comments -o foo.pkl testdata/ontology/tiny_ontology/README

# Good ontology, read comment from file
echo ""
echo "Good ontology, read comment from file"
$SERIALIZE -o foo.pkl testdata/ontology/tiny_ontology < testdata/ontology/tiny_ontology/README

# Good ontology, read comment from file, use default output
echo ""
echo "Good ontology, read comment from file, use default output"
cat testdata/ontology/tiny_ontology/README | $SERIALIZE testdata/ontology/tiny_ontology

# Good ontology, read comment from stdin (interactively)
echo ""
echo "Good ontology, read comment from stdin interactively"
$SERIALIZE -o foo.pkl testdata/ontology/tiny_ontology
