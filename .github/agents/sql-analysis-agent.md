# SQL Analysis Agent

## Purpose
Analyze SQL files and extract:
- Object names (Procedure, Function, Package)
- Table references
- Count of INSERT, UPDATE, DELETE operations

## Output
Generate:
- HTML report
- Email-ready attachment

## Instructions
- Scan all `.sql` files from `/samples`
- Use regex for parsing SQL objects
- Count DML operations
- Generate structured HTML output

## Expected Table Format

| Object Name | Inserts | Updates | Deletes |
|-------------|--------|--------|--------|