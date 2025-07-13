# Design Document: Netskope Customer support

## Overview

This document outlines architecture, design decisions, security and other details

## Architecture Overview

** Tech stack

- **FastPI**
- **PostgreSQL** 
- **SQLALchemy** ORM for translating Python relational objects to DB understandable language
- **Docker** Engine for containerizing the application to make them available as micro services


** DB Schema Design

Please refer to erd_diagram.pdf in the same repo

** API endpoints

A Swagger UI outlinging API endpoints is made available at http:<app_endpoint>/docs.
Please go to the mentioned endpoint once app is launched

** Future work

Current app can be treated as just an enhanced MVP for the requirements. Future improvements may include

- Adding authentication
- Improving DB query time and transaction rollback in case failures
- Revising DB Schema based on requirement changes
- Pen Testing and identifiying Sec loop holes
- Adding Unit tests and Integration tests
- Adding more doc string and comments to explain workflow 
- Adding background scheduler using Celery and redis to send alerts
  in case of SLA breach
- Adding AI assistance for support execs


##  Versioning

| Version | Date       | Author    | Description                |
|:----------|:------------|:------------|:----------------------------|
| 1.0      | 2025-07-12 | Pavan Vemana | Initial design document |