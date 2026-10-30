* [] hactors init
* [x] hactors project create
* [x] hactors workflow create
* [x] hactors create-task — crea tasks/TASK-nnnnn.md con el contador `task` y su cabecera en frontmatter; no declara alcance, entregables ni criterios, y no aprueba la TASK.
* [x] hactors use-run — selecciona la ruta activa completa o asciende al padre; CLI y pruebas verificadas.
* [x] hactors create-rfc-run — crea instancias bajo task_run o plan_run; jerarquía recursiva verificada, no genera documentos RFC.
* [x] hactors create-plan-run — crea y activa instancias bajo rfc_run; jerarquía recursiva verificada, no genera documentos PLAN.
* [x] hactors create-test-run — crea y activa instancias bajo rfc_run inicial o derivado; CLI y pruebas verificadas, no genera ni ejecuta artefactos TEST.
* [x] hactors create-harness-run — crea y activa instancias bajo el test_run solicitante con referencias declaradas; no publica, verifica ni ejecuta recetas HARNESS.
* [x] hactors create-evidence — registra EVD-nnnnn.yaml junto a su origen, declarado o tomado de la instancia activa; no captura el contexto observado ni declara aplicabilidad.
* [x] hactors create-finding — registra FND-nnnnn.yaml junto a su origen, declarado o tomado de la instancia activa; no declara afectados ni acciones.
* [] hactors relate-finding — declara las relaciones de afectación (affects) de un hallazgo existente.
* [x] hactors create-summary — crea el archivo de resumen de una RFC o de un workflow_run con la cabecera en frontmatter y una remisión a SUMMARY_TEMPLATE.md; no redacta sus secciones ni declara su consolidación.
* [] hactors harness create
* [] hactors validate
* [] hactors index
* [] hactors export
* [] hactors transition
* [] hactors render
* [x] definir los identificadores y las transiciones de las fases del resumen — `in-progress` ⇄ `consolidated` con su tabla de actores en LIFECYCLE.md; SUMMARY.md, SUMMARY_TEMPLATE.md y summary_template.yaml ajustados, y RFC.md fija la consolidación en el estado terminal. La CLI no valida la fase.
* [x] migrar GLOSSARY.md a specs/DEFINITIONS.md — ajustado a la fuente de verdad de HACTORS: `FND-nnnnn` en lugar de `FIND-nnnnn`, identificadores de EVIDENCE y DECISION, los artefactos y las instancias de ejecución que faltaban, la nomenclatura de cinco y seis cifras, y el vocabulario de COSA acotado a su proyecto. Referencias a GLOSSARY repuntadas en RFC.md, DECISIONS.md, HACTORS_SYSTEM.md, TASK_TEMPLATE.md y RFC_TEMPLATE.md.
* [] migrar RFC_SYSTEM.md, WORKFLOW.md, PROJECT_STATE.md, RELATIONSHIPS.md, TRANSACTIONS.md, EXCEPTIONS.md y rfc_active.md desde docs/specs/specs/ (repo COSA) a specs/ — citados sin enlace mientras falten.
* [] migrar QUICKSTARTER.md, CHEAT_SHEET.md, LIFECYCLE_DIAGRAMS.md, EXAMPLES.md y TOOLS.md desde docs/specs/docs/ (repo COSA) a docs/ — anunciados sin enlace mientras falten.