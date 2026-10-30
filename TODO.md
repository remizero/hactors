* [] hactors init
* [x] hactors project create
* [x] hactors workflow create
* [x] hactors task create
* [x] hactors use-run — selecciona la ruta activa completa o asciende al padre; CLI y pruebas verificadas.
* [x] hactors create-rfc-run — crea instancias bajo task_run o plan_run; jerarquía recursiva verificada, no genera documentos RFC.
* [x] hactors create-plan-run — crea y activa instancias bajo rfc_run; jerarquía recursiva verificada, no genera documentos PLAN.
* [x] hactors create-test-run — crea y activa instancias bajo rfc_run inicial o derivado; CLI y pruebas verificadas, no genera ni ejecuta artefactos TEST.
* [x] hactors create-harness-run — crea y activa instancias bajo el test_run solicitante con referencias declaradas; no publica, verifica ni ejecuta recetas HARNESS.
* [x] hactors create-evidence — registra EVD-nnnnn.yaml junto a su origen, declarado o tomado de la instancia activa; no captura el contexto observado ni declara aplicabilidad.
* [] hactors finding add
* [] hactors finding relate
* [] hactors harness create
* [] hactors validate
* [] hactors index
* [] hactors export
* [] hactors transition
* [] hactors render
* [] migrar GLOSSARY.md, LIFECYCLE.md, RFC_SYSTEM.md, WORKFLOW.md, PROJECT_STATE.md, RELATIONSHIPS.md, DECISIONS.md y rfc_active.md desde docs/specs/specs/ (repo COSA) a specs/ — citados sin enlace mientras falten.
* [] migrar QUICKSTARTER.md, CHEAT_SHEET.md, LIFECYCLE_DIAGRAMS.md, EXAMPLES.md y TOOLS.md desde docs/specs/docs/ (repo COSA) a docs/ — anunciados sin enlace mientras falten.