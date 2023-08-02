# Migrate to Angular Standalone

Angular CLI provides migration in 15.2:

https://github.com/angular/angular/blob/main/packages/core/schematics/ng-generate/standalone-migration/README.md

Command:

```
ng generate @angular/core:standalone
```

# main.py

Analysis HTML and TypeScript code to provide some hints about modules to import.

This tool may provide some help if standalone-migration misses import informations.

## Options

The script accepts the following options:

* `--scan-component`: scan for component definitions in given folders before check for import hints.
* `-v`: set logging level to `DEBUG`.
