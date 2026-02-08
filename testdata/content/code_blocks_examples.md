# Code Blocks Examples

A comprehensive guide to using code blocks in x-presenter presentations.

---

## Python Examples

Here are some common Python patterns:

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

---

## JavaScript Examples

JavaScript code with modern ES6+ syntax:

```javascript
async function fetchData(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data.results;
    } catch (error) {
        console.error('Failed to fetch:', error);
        return null;
    }
}
```

---

## Bash Script Example

A practical shell script for deployment:

```bash
#!/bin/bash
echo "Deploying application..."
cd /app
git pull origin main
pip install -r requirements.txt
systemctl restart myservice
echo "Deployment complete!"
```

---

## SQL Query Example

Database query with joins and aggregation:

```sql
SELECT u.name, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
WHERE u.is_active = true
GROUP BY u.id, u.name
HAVING COUNT(p.id) > 5
ORDER BY post_count DESC
LIMIT 10;
```

---

## JSON Configuration

Application configuration in JSON format:

```json
{
  "version": "1.0.0",
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false
  },
  "database": {
    "engine": "postgresql",
    "host": "localhost",
    "pool_size": 10
  },
  "features": {
    "caching": true,
    "logging": true
  }
}
```

---

## YAML Configuration

Server configuration in YAML format:

```yaml
server:
  host: 0.0.0.0
  port: 8000
  debug: false

database:
  engine: postgresql
  host: localhost
  pool_size: 10

features:
  caching:
    enabled: true
    ttl_seconds: 3600
```

---

## Java Example

Java class with methods and type annotations:

```java
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public double divide(double numerator, double denominator) {
        if (denominator == 0) {
            throw new IllegalArgumentException("Denominator cannot be zero");
        }
        return numerator / denominator;
    }
}
```

---

## Go Example

Go function with error handling:

```go
func readFile(filename string) ([]byte, error) {
    file, err := os.Open(filename)
    if err != nil {
        return nil, fmt.Errorf("cannot open file: %w", err)
    }
    defer file.Close()
    return ioutil.ReadAll(file)
}
```

---

## Mixed Content Slide

This slide demonstrates code blocks with other content:

Here's a practical example of data processing:

- Load data from CSV file
- Validate each record
- Transform and clean the data
- Export to database

```python
import csv

def process_csv(filename):
    records = []
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if validate_record(row):
                records.append(transform(row))
    return records
```

The processed records are ready for database insertion.

---

## Before and After Refactoring

**Original code with nested loops:**

```python
result = []
for item in items:
    for value in item:
        if value > threshold:
            result.append(value * 2)
```

**Refactored using list comprehension:**

```python
result = [value * 2 for item in items for value in item if value > threshold]
```

---

## Multiple Code Blocks Per Slide

**Backend API endpoint:**

```python
@app.route('/api/data', methods=['POST'])
def get_data():
    request_data = request.get_json()
    result = process_data(request_data)
    return jsonify(result)
```

**Frontend code to call the endpoint:**

```javascript
async function callAPI(data) {
    const response = await fetch('/api/data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return response.json();
}
```

---

## No Language Specified

Code blocks work without a language identifier too:

```
Plain text code block without syntax highlighting.
This is useful for pseudocode or custom formats.
    Indentation is preserved
        Just like in the source
```

---

## Summary

Key features of code blocks in x-presenter:

- Fenced code blocks with triple backticks (` ``` `)
- Optional language identifier for syntax highlighting
- Monospace Courier New 12pt font
- Light gray background for distinction
- Supported languages: Python, JavaScript, Java, Go, Bash, SQL, YAML, JSON
- Automatic height sizing based on line count
- Works alongside text, lists, and images

For more details, visit the [Code Blocks User Guide](../../docs/how-to/using_code_blocks.md).
