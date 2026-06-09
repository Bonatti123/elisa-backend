# Modelos de Datos

## User
Tabla: `users`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | PK |
| username | VARCHAR(150) | Único |
| email | EmailField | |
| first_name | VARCHAR(150) | |
| last_name | VARCHAR(150) | |
| role | FK → Role | |
| is_active | Boolean | |
| is_staff | Boolean | |
| is_superuser | Boolean | |

## Role
Tabla: `roles`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(100) | Único |
| description | Text | |
| permissions | JSON | |
| is_active | Boolean | |

## Purchase
Tabla: `purchases`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | PK |
| provider_name | VARCHAR(255) | |
| document_type | VARCHAR(20) | invoice/receipt/credit_note/debit_note |
| document_number | VARCHAR(100) | |
| amount | Decimal(12,2) | |
| issue_date | Date | |
| category | VARCHAR(100) | |
| attachment | VARCHAR(500) | |
| notes | Text | |
| is_active | Boolean | Soft delete |

## Sale
Tabla: `sales`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | PK |
| client_name | VARCHAR(255) | |
| client_email | EmailField | |
| document_type | VARCHAR(20) | invoice/receipt/credit_note/debit_note |
| document_number | VARCHAR(100) | |
| amount | Decimal(12,2) | |
| issue_date | Date | |
| status | VARCHAR(20) | pending/paid/cancelled/partial |
| category | VARCHAR(100) | |
| notes | Text | |
| is_active | Boolean | Soft delete |
