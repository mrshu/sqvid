# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- docs: Document `table` and `column` in `custom_sql`

## [v0.1.9 - 2020-09-08]
### Added
- add: Ability to set `limit` per validation
- add: Implementation of `limit` for `custom_sql`
- docs: Describe `limit` on per-validation level

## [v0.1.8] - 2020-05-13
### Added
- add: Parameter to limit number of returned rows on fail
- add: Ability to execute validations for a specific table

## [v0.1.7] - 2019-12-12
### Added
- add: handling errors in validation defitions

## [v0.1.6] - 2019-10-28
### Added
- docs: Add examples for validator parameters
- tests: Add a few more end-to-end tests
- docs: Add first version
- docs: Add bages and pin pygments
- add: Ability to set severity
### Changed
- fix: Any non-warn severity defaults to error
- refactor: Evaluation execution loop

## [v0.1.5] - 2019-10-05
### Added
- feat: Include only subset of columns in report
### Changed
- test: Make sure Click tests also check output
- fix: Select from in `unique` validator


## [v0.1.4] - 2019-10-04
### Added
- feat: Add `accepted_values` validator
- feat: Custom (SQL) columns
- feat: Add `not_null` validator
### Changed
-  fix: Make `unique` validator select `column`


## [v0.1.3] - 2019-10-04
### Added
- feat: Add `accepted_values` validator
### Changed
-  fix: Make `unique` validator select `column`


## [v0.1.2] - 2019-10-04
### Changed
- fix: `unique` validator only selects one column


## [v0.1.1] - 2019-09-27
### Added
- Add --verbose option, go for Python 3.6+
- Setup TravisCI and fix README
- First release of sqvid

