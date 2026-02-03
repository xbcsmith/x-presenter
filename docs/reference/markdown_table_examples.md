<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Markdown Table Examples](#markdown-table-examples)
  - [Basic Tables](#basic-tables)
    - [Simple 2x2 Table](#simple-2x2-table)
    - [Simple 3x3 Table](#simple-3x3-table)
  - [Tables with Alignment](#tables-with-alignment)
    - [Left-Aligned Columns](#left-aligned-columns)
    - [Center-Aligned Columns](#center-aligned-columns)
    - [Right-Aligned Columns](#right-aligned-columns)
    - [Mixed Alignment](#mixed-alignment)
  - [Tables with Inline Formatting](#tables-with-inline-formatting)
    - [Bold Text in Cells](#bold-text-in-cells)
    - [Italic Text in Cells](#italic-text-in-cells)
    - [Inline Code in Cells](#inline-code-in-cells)
    - [Combined Formatting](#combined-formatting)
  - [Edge Cases](#edge-cases)
    - [Single Column Table](#single-column-table)
    - [Single Row Table](#single-row-table)
    - [Empty Cells](#empty-cells)
    - [Wide Table (Many Columns)](#wide-table-many-columns)
    - [Tall Table (Many Rows)](#tall-table-many-rows)
  - [Real-World Examples](#real-world-examples)
    - [Project Timeline](#project-timeline)
    - [Test Results](#test-results)
    - [API Endpoints](#api-endpoints)
    - [Comparison Table](#comparison-table)
  - [Tables in Context with Other Content](#tables-in-context-with-other-content)
    - [Mixed Content Example](#mixed-content-example)
      - [Performance Metrics](#performance-metrics)
  - [Notes](#notes)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Markdown Table Examples

This document provides examples of Markdown tables for testing and reference
purposes in the x-presenter project.

## Basic Tables

### Simple 2x2 Table

| Header 1 | Header 2 |
| -------- | -------- |
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

### Simple 3x3 Table

| Column A | Column B | Column C |
| -------- | -------- | -------- |
| A1       | B1       | C1       |
| A2       | B2       | C2       |
| A3       | B3       | C3       |

## Tables with Alignment

### Left-Aligned Columns

| Name  | Age | City          |
| :---- | :-- | :------------ |
| Alice | 30  | New York      |
| Bob   | 25  | Los Angeles   |
| Carol | 35  | San Francisco |

### Center-Aligned Columns

|  Product  | Price  | Rating |
| :-------: | :----: | :----: |
|  Widget   | $10.99 |  4.5   |
|  Gadget   | $25.50 |  4.8   |
| Doohickey | $15.00 |  4.2   |

### Right-Aligned Columns

| Item    | Quantity |  Total |
| :------ | -------: | -----: |
| Apples  |       12 | $15.00 |
| Bananas |        8 | $12.00 |
| Oranges |       15 | $22.50 |

### Mixed Alignment

| Product Name |   Description    |  Price | Stock |
| :----------- | :--------------: | -----: | :---: |
| Laptop       | High performance | $1,299 |  15   |
| Mouse        |     Wireless     | $29.99 |  50   |
| Keyboard     |    Mechanical    | $89.99 |  25   |

## Tables with Inline Formatting

### Bold Text in Cells

| Feature      | Status      | Priority |
| ------------ | ----------- | -------- |
| **Login**    | Complete    | **High** |
| **Checkout** | In Progress | **High** |
| Profile      | Planned     | Medium   |

### Italic Text in Cells

| Book Title              | Author              | Year |
| ----------------------- | ------------------- | ---- |
| _1984_                  | George Orwell       | 1949 |
| _To Kill a Mockingbird_ | Harper Lee          | 1960 |
| _The Great Gatsby_      | F. Scott Fitzgerald | 1925 |

### Inline Code in Cells

| Function  | Description        | Return Type |
| --------- | ------------------ | ----------- |
| `print()` | Outputs to console | `None`      |
| `len()`   | Returns length     | `int`       |
| `range()` | Creates sequence   | `range`     |

### Combined Formatting

| Component      | Type           | Status        |
| -------------- | -------------- | ------------- |
| **`Button`**   | _UI Element_   | **Complete**  |
| **`Input`**    | _Form Control_ | **Complete**  |
| **`Dropdown`** | _Form Control_ | _In Progress_ |

## Edge Cases

### Single Column Table

| Status   |
| -------- |
| Active   |
| Inactive |
| Pending  |

### Single Row Table

| Name  | Age | Role      | Department  |
| ----- | --- | --------- | ----------- |
| Alice | 30  | Developer | Engineering |

### Empty Cells

| Name  | Phone    | Email               |
| ----- | -------- | ------------------- |
| Alice | 555-0100 | <alice@example.com> |
| Bob   |          | <bob@example.com>   |
| Carol | 555-0102 |                     |

### Wide Table (Many Columns)

| ID  | Name  | Dept | Role | Salary | Start Date | Status |
| --- | ----- | ---- | ---- | ------ | ---------- | ------ |
| 001 | Alice | Eng  | Dev  | $120K  | 2020-01-15 | Active |
| 002 | Bob   | Mkt  | Mgr  | $95K   | 2021-03-10 | Active |

### Tall Table (Many Rows)

| Product ID | Product Name |
| ---------- | ------------ |
| P001       | Widget A     |
| P002       | Widget B     |
| P003       | Widget C     |
| P004       | Widget D     |
| P005       | Widget E     |
| P006       | Widget F     |
| P007       | Widget G     |
| P008       | Widget H     |
| P009       | Widget I     |
| P010       | Widget J     |

## Real-World Examples

### Project Timeline

| Milestone       | Start Date | End Date   | Status      | Owner |
| :-------------- | :--------- | :--------- | :---------- | :---- |
| **Planning**    | 2024-01-01 | 2024-01-31 | Complete    | Alice |
| **Development** | 2024-02-01 | 2024-04-30 | In Progress | Bob   |
| **Testing**     | 2024-05-01 | 2024-05-31 | Pending     | Carol |
| **Deployment**  | 2024-06-01 | 2024-06-15 | Pending     | David |

### Test Results

| Test Case           | Expected |  Actual   |  Status  |
| :------------------ | :------: | :-------: | :------: |
| User Login          | Success  |  Success  |   Pass   |
| Password Reset      | Success  |  Success  |   Pass   |
| Invalid Credentials |  Error   |   Error   |   Pass   |
| Session Timeout     | Redirect | **Error** | **Fail** |

### API Endpoints

| Method   | Endpoint         | Description     | Auth Required |
| :------- | :--------------- | :-------------- | :-----------: |
| `GET`    | `/api/users`     | List all users  |      Yes      |
| `POST`   | `/api/users`     | Create new user |      Yes      |
| `GET`    | `/api/users/:id` | Get user by ID  |      Yes      |
| `PUT`    | `/api/users/:id` | Update user     |      Yes      |
| `DELETE` | `/api/users/:id` | Delete user     |      Yes      |

### Comparison Table

| Feature       | Free Plan | Pro Plan | Enterprise |
| :------------ | :-------: | :------: | :--------: |
| Storage       |   5 GB    |  100 GB  | Unlimited  |
| Users         |     1     |    10    | Unlimited  |
| **Support**   |   Email   | Priority |  **24/7**  |
| API Access    |    No     |   Yes    |    Yes     |
| Custom Domain |    No     |   Yes    |    Yes     |
| Analytics     |   Basic   | Advanced |  Advanced  |

## Tables in Context with Other Content

### Mixed Content Example

This slide demonstrates a table integrated with other Markdown elements.

**Key Points:**

- Tables integrate seamlessly with paragraphs
- Lists can appear before or after tables
- Headers organize content sections

#### Performance Metrics

| Metric      |    Q1 |    Q2 |    Q3 |    Q4 |
| :---------- | ----: | ----: | ----: | ----: |
| Revenue     | $100K | $125K | $150K | $175K |
| Users       | 1,000 | 1,500 | 2,200 | 3,000 |
| Growth Rate |   25% |   25% |   47% |   36% |

**Conclusions:**

1. Steady revenue growth across all quarters
2. User acquisition accelerated in Q3
3. Target exceeded by 15%

## Notes

These examples demonstrate the variety of tables that the x-presenter converter
should handle. Implementation should prioritize:

- Standard table syntax (pipes and dashes)
- Column alignment (left, center, right)
- Inline formatting (bold, italic, code)
- Professional default styling
