# Changelog

## [1.0] - 2021-03-13
### Added
- Initial release of Valditor Toolkot

## [1.1] - 2021-04-05
### Fixed
- Found missing line numbers
- Found missing reports
- Allow data type to be a subclass of data type in property constraint
- Handle conflicting namespaces in ontology and data
- Reject pickle file whose Version does not match the Toolkit Version
- Fixed regex to match @type statement in json-ld files

### Changed
- Toolkit document

### Added
- Changelog file


## [1.2] - 2021-06-05
### Fixed
- Fixed error messages to flag ordered lists (olo) as an UnsupportedFeature
- Fixed validator to flag unknown properties as errors
