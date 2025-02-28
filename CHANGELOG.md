# Changelog

*Changelog created using the [Simple Changelog](https://marketplace.visualstudio.com/items?itemName=tobiaswaelde.vscode-simple-changelog) extension for VS Code.*

## [Unreleased]

-

## [1.0.1] - 2025-02-26

### Added

- icon.png and fanart.png to represent a boxer theme

### Changed

- Removed all Python 2 compatibility code (six.PY2 checks).
- Replaced `xbmc.translatePath()` with `xbmcvfs.translatePath()` for Kodi 19+ compatibility.
- Removed `six` import (no longer needed in Python 3).
- Refactored `favorites_import()` for cleaner logic and safer file handling.
- General code cleanup for improved maintainability.