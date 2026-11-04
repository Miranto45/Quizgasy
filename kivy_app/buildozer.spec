[app]
title = Fanontaniana
package.name = fanontaniana
package.domain = mg.miranto
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy
android.permissions = INTERNET
orientation = portrait
fullscreen = 0

# Architecture moderne (la grande majorite des telephones actuels)
android.archs = arm64-v8a

# Correctif du bug "charset_normalizer wheel not supported"
# (voir kivy/buildozer issue #2051 - corrige sur la branche develop de p4a)
p4a.branch = develop

log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
