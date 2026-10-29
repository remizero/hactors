las siguientes ideas descritas en este documento aún no son normativas, sino un esbozo de la idea que representa un Harness.

Un harness de verificación tiene un alcance determinado. Cuando ese alcance deja de ser suficiente para verificar un nuevo comportamiento, no se modifica el harness existente para incorporar el nuevo alcance; se crea un nuevo harness, con identidad y trazabilidad propias.


## scope
Cada harness debe declarar explícitamente qué pretende comprobar.

```
HRN-00001

Purpose:
  Verify supervisor retention after child termination.

Scope:
  Process lifecycle + supervisor survival.

Out of scope:
  Credential transition
  SHM cleanup
  IPC authorization

Used by:
  TEST-00001
```

Un harness puede evolucionar solo dentro de su scope.
Es decir:

```
HRN-00001
  v1
  v2
  v3
```

## que debe producir un Harness

```
HRN-00001
 ├── source revision
 ├── build identity
 ├── configuration
 ├── test identity
 └── evidence
```

## que debería permitir
algo similar a esto, no definitivo ni normativo

```
RFC-F00001
│
├── Objective O1
│    └── TEST-00001
│         └── HRN-00001
│              └── EVD-00001
│
├── Objective O2
│    └── TEST-00002
│         └── HRN-00002
│              └── EVD-00002
│
└── Objective O3
     └── TEST-00003
          └── HRN-00003
               └── EVD-00003
```

## Verification Harness Isolation Rule

Cada harness debe tener un alcance de verificación explícito. Un cambio que amplíe, altere o sustituya dicho alcance requiere un nuevo harness con identidad propia. Las evidencias generadas por un harness quedan vinculadas a la versión concreta del harness y a su artefacto de ejecución.

No harness mutation across verification scopes.

El formato normativo del artefacto se define en [templates/HRN_TEMPLATE.md](templates/HRN_TEMPLATE.md).

