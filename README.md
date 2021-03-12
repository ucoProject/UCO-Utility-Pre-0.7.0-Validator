# UCO-Utility-Pre-0.6.0-Validator

## Description -  (Alpha Release)

The UCO/CASE Validation Toolkit provides the capability to validate JSON-LD data files against a turtle-file based ontology such as the Unified Cyber Ontology (UCO) and Cyber-Investigation Analysis Standard Expression (CASE).

Note - this tool has a number of suggested improvements that may be added in the future. Among these, the tool may present error messages that could be viewed by some as warnings vs errors in ontological representation.

## Getting Started

### Dependencies:
* Preferred operating system: linux
* alternate operating system: windows
* python version 3.6.8 or newer
* git
* pip
* virtualenv

There are minor toolkit setup differences between Linux and Windows, described here:


### Installing - Linux

1.  Create empty working directory
* $ mkdir foo
* $ cd foo

2.  Copy source files into the working directory
* $ git clone https://gitlab.mitre.org/sbernste/enhanced-case-toolkit.git

3.  In the tookit directory, create a python3 virtual environment
* $ cd enhanced-case-toolkit
* $ virtualenv --python=python3 venv

4.  Activate the virtual environment
* $ source venv/bin/activate

5.  Install the source into the virtual environment
* $ pip install --upgrade pip
* $ pip install --editable src

6.  Run python commands


### Installing - Windows

1. Create empty working directory
 * mkdir foo
2. Copy source files
 *  cd foo
 * `foo>` git clone https://gitlab.mitre.org/sbernste/enhanced-case-toolkit.git
3. Create virtual environment
 * `foo>` cd enhanced_case_toolkit
 * `foo\enhanced-case-toolkit>` virtualenv --python=python3 venv
4. Activate the virtual environment
 * `foo\enhanced-case-toolkit>` venv\Scripts\activate
5. Install the source
 * `(venv) foo\enhanced-case-toolkit>` pip install --editable src
6. Run the scripts from src directory, for example:
 * `(venv) foo\enhanced-case-toolkit>` cd src
 * `(venv) foo\enhanced-case-toolkit\src>` python validate.py ..\data\ontology-0.4.0\ontology ..\data\samples-0.4\accounts.json
7. When done, deactivate the virtual environment
 * `(venv) foo\enhanced-case-toolkit>` deactivate

## Executing the tool

As long as the virtual environment is activated, you can now run these scripts.

   -------------------------------------------------------------------
> validate ontology_path jsonld_path [jsonld_path...]

Validate json-ld data against an ontology
* ontology_path:   path to serialized ontology file or directory containing turtle files.
* jsonld_path:     path to json-ld file or serialized json-ld file.



   ------------------------------------------------------------------------------------------
> v4to5 [-o output_filepath] input_filepath

Convert version UCO 0.4 json-ld data to UCO 0.5
* input_filepath   path to version 0.4 jsonld data file
* output_filepath  path to output version 0.5 jsonld data file [default: STDOUT]

   --------------------------------------------------------------------------
 > serialize [-c comment] [-o output_filepath] input_filepath

Serialize ontology or json-ld file

* comment:         description to include in serialized file [default: read from stdin].
* output_filepath: path to write serialized file [default: input_filepath.pkl].
* input_filepath:  path to json-ld file or directory containing turtle files.



   --------------------------------------------
>    describe serialized_filepath

Describe serialized file
* serialized_filepath:  path to serialized file.
