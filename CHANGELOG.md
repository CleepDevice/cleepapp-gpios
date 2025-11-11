# Changelog

## [1.3.0] - 2025-11-11

### Fixed
- Input does not work as expected
- There were issues restoring gpio state
- Fix issue with inverted state

### Changed
- Code improvements
- Send "on" state on on/off events to facilitate device state sync
- Properly handle volatile gpio state (not store in config file)

## [1.2.1] - 2024-11-21

### Fixed
- Fix status turning on/off output
- Fix odd/even pins on gpios ui component that was inversed

## [1.2.0] - 2024-10-16

### Changed
- Migrate to Cleep components

## [1.1.3] - 2021-07-31

### Changed
- Frontend service doesn't have to catch update events

## [1.1.2] - 2021-06-08

### Changed
- Improve command parameters check

### Fixed
- Fix issue at startup with gpio configured

## [1.1.1] - 2021-05-16

### Changed
- Backend: migrate to python3
- Backend: update after core changes
- Backend: improve unit tests + fix small issues
- Frontend: code update

## [1.1.0] - 2021-04-08

### Changed
- Improve robustness adding unit tests
- Add documentation generation
- Update after core changes
- Fox some issues

## [1.0.0] - 2019-02-16

### Changed
- First release

