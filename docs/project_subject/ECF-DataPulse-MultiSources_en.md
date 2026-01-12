# ECF: Multi-Source Data Pipeline

## Professional Title: Data Engineer – RNCP35288
### Assessed Skills: C1.1, C1.3, C1.4

---

## Professional Context

You are hired as a **Data Engineer** at **DataPulse Analytics**, a startup specialized in multi-source data aggregation and analysis.

The CTO assigns you the following mission:

> *“We need a platform capable of collecting data from several heterogeneous sources: websites, APIs, and partner files. These data must be stored, cleaned, and made available to our analysts. I am counting on you to propose a suitable architecture and implement it.”*

---

## Specifications

### Objective

Design and implement a **data collection and analysis platform** that meets the following requirements:

### Functional Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| FR1 | Collect data from **at least 2 websites** via scraping | Mandatory |
| FR2 | Collect data from **at least 1 REST API** | Mandatory |
| FR3 | Import data from **1 provided Excel file** | Mandatory |
| FR4 | Store raw data in a persistent way | Mandatory |
| FR5 | Clean and transform collected data | Mandatory |
| FR6 | Make data queryable via SQL | Mandatory |
| FR7 | Enable cross-source analysis | Optional |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| NFR1 | Respect scraping legality (authorized sites only) | Mandatory |
| NFR2 | Comply with GDPR for personal data | Mandatory |
| NFR3 | Document the technical architecture | Mandatory |
| NFR4 | Containerize the infrastructure (Docker) | Mandatory |
| NFR5 | Ensure pipeline reproducibility | Optional |
| NFR6 | Error handling and recovery | Optional |

---

## Available Data Sources

### 1. Websites – Scraping Authorized

The following sites are **explicitly designed for scraping learning** and display the message *“We love being scraped!”*:

| Site | URL | Content |
|-----|-----|---------|
| **Books to Scrape** | https://books.toscrape.com | Fictional bookstore: 1000 books, prices, ratings, categories, images |
| **Quotes to Scrape** | https://quotes.toscrape.com | Quotes: text, authors, tags |
| **E-commerce Test** | https://webscraper.io/test-sites/e-commerce/allinone | Electronic products: laptops, phones, specs |

You must use **at least 2 of these 3 sites**.

### 2. Open Data API

| API | URL | Documentation |
|-----|-----|---------------|
| **Address API** (Geocoding) | https://api-adresse.data.gouv.fr/search/ | https://adresse.data.gouv.fr/api-doc/adresse |

**Example request:**
```bash
curl "https://api-adresse.data.gouv.fr/search/?q=20+avenue+de+Segur+Paris&limit=1"
```

**Response:**
```json
{
  "features": [{
    "geometry": {"coordinates": [2.308628, 48.850699]},
    "properties": {
      "label": "20 Avenue de Ségur 75007 Paris",
      "score": 0.95,
      "city": "Paris",
      "postcode": "75007"
    }
  }]
}
```

**Rate limit:** 50 requests/second

### 3. Partner File (Provided)

The file `partenaire_librairies.xlsx` contains a list of 20 partner bookstores:

| Column | Type | Example | GDPR Sensitivity |
|-------|------|---------|-----------------|
| nom_librairie | string | "Librairie du Marais" | Public |
| adresse | string | "15 rue des Francs-Bourgeois" | Public |
| code_postal | string | "75004" | Public |
| ville | string | "Paris" | Public |
| contact_nom | string | "Marie Dubois" | **Personal Data** |
| contact_email | string | "m.dubois@librairie.fr" | **Personal Data** |
| contact_telephone | string | "0142789012" | **Personal Data** |
| ca_annuel | float | 385000 | Confidential |
| date_partenariat | date | "2021-03-15" | Public |
| specialite | string | "Literature" | Public |

⚠️ **Warning**: This file contains personal data that must be processed in compliance with GDPR.

---

## Requested Work

### Part 1: Architecture Design

**Assessed Skill: C1.1**

You must **design and justify** a technical architecture adapted to the stated needs.

#### Deliverable 1.1: Technical Architecture Document (TAD)

Write a document answering the following questions:

**1. Overall Architecture Choice**
- What architecture do you propose? (Data Lake, Data Warehouse, Lakehouse, NoSQL database, other?)
- Why did you choose this architecture over an alternative?
- What are the advantages and disadvantages of your choice?

**2. Technology Choices**
- Which technologies do you use for raw data storage? Justify your choice.
- Which technologies do you use for transformed data? Justify your choice.
- Which technologies do you use for SQL querying? Justify your choice.
- Compare with at least one alternative for each choice.

**3. Data Organization**
- How do you organize data within your architecture?
- Do you propose transformation layers? Which ones and why?
- What naming convention do you adopt?

**4. Data Modeling**
- What data model do you propose for the final layer?
- Provide a schema (entity-relationship diagram or other)
- Justify your modeling choices

**5. GDPR Compliance**
- Which personal data do you identify in the sources?
- What protection measures do you propose?
- How do you manage the right to erasure?

#### Deliverable 1.2: Docker Infrastructure

Provide a functional `docker-compose.yml` file implementing your architecture.
---
### Part 2: Data Collection

**Assessed Skill: C1.3**

#### Deliverable 2.1: Web Scrapers

Develop scrapers for **at least 2 websites** among the 3 proposed.

**Technical requirements:**
- Politeness delay between requests (minimum 1 second)
- Identifiable User-Agent
- HTTP error handling
- Full pagination handling

**Minimum data to extract:**

*Books to Scrape:*
- Title, price, rating (1–5 stars), availability, category

*Quotes to Scrape:*
- Quote text, author, tags

*E-commerce Test:*
- Product name, price, description, category

#### Deliverable 2.2: API Client

Develop a client for the Address API to geocode partner bookstore addresses.

**Requirements:**
- Compliance with the rate limit
- Handling of addresses not found

#### Deliverable 2.3: Excel File Import

Develop an import module for the partner file with:
- Format validation
- **Personal data processing compliant with GDPR** (anonymization, pseudonymization, or deletion)
- Storage compliant with your architecture

#### Deliverable 2.4: GDPR Documentation

Provide a document `RGPD_CONFORMITE.md` containing:
- Inventory of collected personal data
- Legal basis for processing for each data item
- Implemented protection measures
- Deletion procedure upon request

---
### Part 3: ETL Pipeline

**Assessed Skill: C1.4**

#### Deliverable 3.1: Transformations

Implement the necessary transformations to go from raw data to usable data.

**Examples of expected transformations:**

- Currency conversion (£ → €, $ → €)
- Format normalization (dates, text)
- Outlier removal
- Deduplication
- Data enrichment (geocoding of addresses)

#### Deliverable 3.2: Loading

Implement the loading of the transformed data into your SQL query solution:
- Schema creation
- Data loading
- Creation of necessary indexes

#### Deliverable 3.3: Orchestration

Provide a script to execute the entire pipeline, with the option to run each step separately.

#### Deliverable 3.4: Analytical Queries

Provide an `analyses.sql` file containing **5 queries** demonstrating the value of your platform:

1. A simple aggregation query
2. A query with a join function
3. A query with a window function
4. A top-N ranking query
5. A query combining at least two data sources

---
### Bonus

| Bonus | Points |

|-------|--------|
| Image Download | +2 |

| Structured Logging | +2 |

| Developer Documentation | +2 |

---

## Expected Deliverables
```
ecf-{nom}/
├── docker-compose.yml
├── requirements.txt
├── README.md
│
├── docs/
│   ├── DAT.md                    # Dossier Architecture Technique
│   └── RGPD_CONFORMITE.md        # Conformité RGPD
│
├── src/
│   └── # ... votre code organisé librement
│
├── sql/
│   └── analyses.sql
│
└── data/
    └── partenaire_librairies.xlsx  # Fichier fourni
```

---

## File Provided

The file `partenaire_librairies.xlsx` contains 20 partner bookstores with the columns described above.

---

**Good luck!**