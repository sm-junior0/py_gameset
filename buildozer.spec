[app]
title = FarmQuest
package.name = farmquest
package.domain = org.example.farmquest
source.dir = .
source.include_exts = py,kv,json,png,jpg,jpeg,wav,ogg,ttf,txt,md
version = 0.1.0
requirements = python3,kivy==2.3.1
orientation = landscape
fullscreen = 0

# The prototype is offline and does not require special Android permissions.
android.permissions =

# Keep the default debug build flow for prototype APK generation.
buildozer.spec_version = 1.5.0

[buildozer]
log_level = 2
warn_on_root = 1

# Buildozer packaging must run on Linux, macOS, or Windows via WSL.
