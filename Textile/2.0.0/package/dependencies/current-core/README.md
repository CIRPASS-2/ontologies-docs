# Core Ontology (CO)
The CIRPASS-2 European Project EU DPP Core Ontology

## Overview

The **EU DPP CORE ontology** is modular, with single namespace https://w3id.org/eudpp.
The modular stucture of the ontology is given as follows:

```
EU DPP CORE
├── CON
├── P_DPP
├── ACTOR
├── SOC
├── LCA
├── EVENT
├── COMP
├── IDENT
├── MAT
└── ...
```

### Modules
The **EU DPP CORE ontology** imports the connector and several modules that define specific parts of the ontology model. 

- **EU DPP CORE** – the ontology integrating the modules.
- **CON** – the Connector; a special bridge module defining cross-module relationships and integration axioms.
- **P_DPP** – the module describing the Product and Digital Product Passport concepts.
- **ACTOR** – the module describing Economic Operators (EO), Actors, Roles, and related concepts. 
- **SOC** – the module describing substances of concern related to the Product.
- **LCA** –  the module describing Life-Cycle Assessment.
- **EVENT** –  the module describing Events connected to  Product and DPP.
- **COMP** –  the module describing compliance aspects related to Product and DPP.
- **IDENT** –  the module describes identifiers used in the EU DPP CO delivered by the CIRPASS-2 European Project.
- **MAT** –  the module provides a placeholder (a general module) under which sectors can establish their specific structure for materials according to the needs of their domain. 
- *(additional modules may be added)*

Filenames for these modules are according to the module name but in lowercase. 

---

© CIRPASS-2 Consortium, 2024-2027

<img width="832" height="128" alt="image" src="https://raw.githubusercontent.com/CIRPASS-2/assets/main/images/cc-commons.png" />

The CIRPASS-2 project receives funding under the European Union's DIGITAL EUROPE PROGRAMME under the GA No 101158775.

**Important disclaimer:**
All software and artifacts produced by the CIRPASS-2 consortium are designed for exploration and are provided for information purposes only. They should not be interpreted as being either complete, exhaustive, or normative. The CIRPASS-2 consortium partners are not liable for any damage that could result from making use of this information. Technical interpretations of the European Digital Product Passport system expressed in these artifacts are those of the author(s) only and do not necessarily reflect those of the European Union, European Commission, or the European Health and Digital Executive Agency (HADEA). Neither the European Union, the European Commission nor the granting authority can be held responsible for them. Technical interpretations of the European Digital Product Passport system expressed in these artifacts are those of the author(s) only and should not be interpreted as reflecting those of CEN-CENELEC JTC 24.


## License

This project is licensed under the Apache License 2.0.

```
Copyright 2024-2027 CIRPASS-2

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
