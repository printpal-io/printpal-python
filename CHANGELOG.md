# Changelog

All notable changes to the PrintPal Python client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-02-03

### Fixed

- Quality parameter now properly passes through the call chain (`generate_and_download` -> `wait_and_download` -> `wait_for_completion`) for correct auto-timeout calculation
- Previously, auto-timeout was incorrectly defaulting to 120 seconds regardless of quality level because quality wasn't being passed through

## [1.0.2] - 2025-02-03

### Changed

- Quality-aware timeouts: `wait_for_completion` and `generate_and_download` now automatically use appropriate timeouts based on quality level
  - default/high: 2-3 minutes
  - ultra: 5 minutes
  - super: 6 minutes
  - superplus: 8 minutes
  - super_texture/superplus_texture: 10 minutes
- Updated estimated generation times to match actual production values
- Added `GENERATION_TIMEOUTS` constant for users who want to customize timeouts

### Fixed

- Fixed timeout errors when using super, superplus, and texture quality levels (previously defaulted to 60 seconds which was too short)

## [1.0.1] - 2025-02-03

### Changed

- Default output format changed from GLB to STL for better 3D printing compatibility
- Smart filename handling: when output_path has a recognized extension (stl, glb, obj, ply, fbx), that format is automatically used
- Extension correction: if requested format differs from filename extension, the extension is corrected to prevent corrupted/misleading files

### Fixed

- Filename extension now always matches actual file format to prevent user confusion

## [1.0.0] - 2025-02-03

### Added

- Initial release of the PrintPal Python client
- Full support for image-to-3D generation
- Full support for text-to-3D generation
- All quality levels: default, high, ultra, super, super_texture, superplus, superplus_texture
- All output formats: STL, GLB, OBJ, PLY, FBX
- Credit balance checking
- Usage statistics
- Pricing information
- Async/polling workflow support
- Comprehensive error handling
- Example scripts for common use cases
