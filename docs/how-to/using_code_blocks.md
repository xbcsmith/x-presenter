<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Using Code Blocks](#using-code-blocks)
  - [Basic Code Block](#basic-code-block)
  - [Syntax](#syntax)
  - [Supported Languages](#supported-languages)
  - [Examples](#examples)
    - [Python](#python)
    - [JavaScript](#javascript)
    - [Bash](#bash)
    - [SQL](#sql)
    - [JSON](#json)
  - [Features](#features)
    - [Monospace Font](#monospace-font)
    - [Syntax Highlighting](#syntax-highlighting)
    - [Background Color](#background-color)
    - [Preserved Formatting](#preserved-formatting)
    - [Auto Sizing](#auto-sizing)
  - [Best Practices](#best-practices)
    - [Keep Code Blocks Short](#keep-code-blocks-short)
    - [Use Meaningful Names](#use-meaningful-names)
    - [Add Comments](#add-comments)
    - [Match Your Audience](#match-your-audience)
    - [Test Your Examples](#test-your-examples)
  - [Limitations](#limitations)
    - [No Line Numbers](#no-line-numbers)
    - [No Scrolling](#no-scrolling)
    - [Single Background Color](#single-background-color)
    - [Fixed Font](#fixed-font)
  - [Combining with Other Slide Elements](#combining-with-other-slide-elements)
  - [Common Patterns](#common-patterns)
    - [Before and After](#before-and-after)
    - [Multiple Language Comparison](#multiple-language-comparison)
    - [Configuration Files](#configuration-files)
  - [Troubleshooting](#troubleshooting)
    - [Code Not Highlighted](#code-not-highlighted)
    - [Code Block Cut Off](#code-block-cut-off)
    - [Indentation Looks Wrong](#indentation-looks-wrong)
    - [Language Not Supported](#language-not-supported)
  - [Next Steps](#next-steps)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Using Code Blocks

Code blocks allow you to display formatted source code in your presentations
with syntax highlighting, proper indentation, and a distinctive background.

## Basic Code Block

Create a code block using triple backticks with an optional language identifier:

```python
def greet(name):
    return f"Hello, {name}!"
```

The language identifier tells x-presenter which syntax highlighting rules to
apply.

## Syntax

Code blocks use standard Markdown fenced code block syntax:

````markdown
```language
your code here
```
````

Replace `language` with the programming language of your code (see Supported
Languages below for options).

## Supported Languages

x-presenter supports syntax highlighting for the following languages:

- **Python**: `python`
- **JavaScript**: `javascript` or `js`
- **Java**: `java`
- **Go**: `go` or `golang`
- **Bash**: `bash` or `shell`
- **SQL**: `sql`
- **YAML**: `yaml`
- **JSON**: `json`

If you use a language not listed above or omit the language identifier, the code
will render with default formatting (no syntax highlighting).

## Examples

### Python

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Call the function
result = fibonacci(10)
print(result)
```

### JavaScript

```javascript
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

const products = [
  { name: "Laptop", price: 999 },
  { name: "Mouse", price: 25 },
];
```

### Bash

```bash
#!/bin/bash
echo "Deploying application..."
cd /app
git pull origin main
pip install -r requirements.txt
systemctl restart myservice
```

### SQL

```sql
SELECT users.name, COUNT(orders.id) as order_count
FROM users
LEFT JOIN orders ON users.id = orders.user_id
GROUP BY users.id
ORDER BY order_count DESC;
```

### JSON

```json
{
  "version": "1.0.0",
  "settings": {
    "debug": false,
    "timeout": 30
  },
  "servers": ["prod-1", "prod-2", "prod-3"]
}
```

## Features

### Monospace Font

Code blocks use Courier New 12pt font to maintain consistent indentation and
readability.

### Syntax Highlighting

Each language has specific color rules for different syntax elements:

- **Keywords**: Purple (e.g., `def`, `function`, `return`)
- **Strings**: Orange (text in quotes)
- **Numbers**: Green (numeric literals)
- **Comments**: Gray (explanatory text)
- **Operators**: Default color (=, +, -, etc.)

### Background Color

Code blocks have a light gray background to distinguish them from regular text
and make them stand out on your slides.

### Preserved Formatting

Indentation, line breaks, and spacing are preserved exactly as you type them.
This is important for languages like Python where indentation has meaning.

### Auto Sizing

Code block height automatically adjusts based on the number of lines:

- Minimum height: 1 inch (for short snippets)
- Maximum height: 4 inches (to prevent overflow)
- Height per line: 0.25 inches

Very long code blocks will be capped at the maximum height.

## Best Practices

### Keep Code Blocks Short

Aim for 10-15 lines maximum per code block. Shorter code snippets:

- Are easier to read on slides
- Don't overwhelm your audience
- Fit better on the slide
- Are easier to explain verbally

If you need to show more code, split it across multiple slides or multiple code
blocks.

### Use Meaningful Names

Write code examples with clear variable and function names:

Good:

```python
def calculate_order_total(items):
    return sum(item.price for item in items)
```

Less clear:

```python
def calc(x):
    return sum(i.p for i in x)
```

### Add Comments

Use inline comments to explain non-obvious code:

```python
# Calculate compound interest
principal = 1000
rate = 0.05
years = 10
amount = principal * (1 + rate) ** years
```

### Match Your Audience

Show code examples relevant to your audience's interests:

- For a Python audience: show Python examples
- For a DevOps presentation: show shell scripts and configuration
- For a data science talk: show data processing examples

### Test Your Examples

Make sure your code examples actually work. A code block with syntax errors or
incomplete logic will confuse your audience.

## Limitations

### No Line Numbers

Code blocks do not include line numbers in the margin. If you need to reference
specific lines, mention them in your speaker notes or verbally during the
presentation.

### No Scrolling

Code blocks are rendered as static images in PowerPoint. If your code block is
very long, it will be capped at the maximum height and may not show all lines.
Solution: Split long code across multiple slides.

### Single Background Color

All code blocks in your presentation use the same background color. The default
is light gray, which works well on most backgrounds.

### Fixed Font

Code blocks always use Courier New font. Other fonts are not currently
supported.

## Combining with Other Slide Elements

Code blocks work well with other slide elements. Here's an example of a slide
with mixed content:

````markdown
## API Implementation

Here's how to use our new API endpoint:

- Call the endpoint with a JSON payload
- Handle the response status codes
- Retry on 429 (rate limited) errors

```python
import requests

response = requests.post(
    "https://api.example.com/data",
    json={"query": "search_term"},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    print(data)
```
````

The API returns results in milliseconds.

This creates a slide with:

1. Title: "API Implementation"
2. Bullet point list with 3 items
3. Code block with Python example
4. Closing text

## Common Patterns

### Before and After

Show a problem and solution:

````markdown
## Refactoring

**Before:**

```python
result = x + y * z / (a - b) * 100
```

**After:**

```python
subtraction = a - b
multiplication = y * z
division = multiplication / subtraction
result = x + (division * 100)
```
````

### Multiple Language Comparison

Show the same logic in different languages:

````markdown
## Hello World

**Python:**

```python
print("Hello, World!")
```

**JavaScript:**

```javascript
console.log("Hello, World!");
```

**Bash:**

```bash
echo "Hello, World!"
```
````

### Configuration Files

Show example configuration or setup:

````markdown
## Configuration

Create a `.env` file:

```yaml
DATABASE_URL: postgresql://user:pass@localhost/mydb
API_KEY: your-api-key-here
DEBUG: false
TIMEOUT: 30
```
````

## Troubleshooting

### Code Not Highlighted

If your code appears without colors, check:

1. Is the language identifier spelled correctly?
2. Is it a supported language (see Supported Languages section)?
3. Try using `text` as the language for plain text display

### Code Block Cut Off

If your code block is cut off at the bottom:

1. Reduce the number of lines in the code block
2. Use a smaller example or split across multiple slides
3. The maximum height is 4 inches per code block

### Indentation Looks Wrong

Make sure you're using consistent indentation (spaces, not tabs):

```python
# Good - consistent spaces
def example():
    if True:
        print("Indentation is correct")
```

### Language Not Supported

If you need a language that's not currently supported:

1. Contact the x-presenter maintainers
2. Use the `text` language identifier as a workaround
3. Check the implementation documentation for the complete language support list

## Next Steps

For more information about x-presenter features, see:

- [Using Slide Layouts](using_slide_layouts.md)
- [Using Speaker Notes](using_speaker_notes.md)
- [Main README](../../README.md)
