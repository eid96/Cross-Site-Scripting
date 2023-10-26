# Cross-Site-Scripting
Task:
Web Application Development:

Set up a Flask (or similar) web application.
Choose a theme or domain for your application (e.g., an online store, blog platform, social network, etc.).
Implement a feature where users can input and store data (e.g., user profiles, product listings, blog posts, comments, reviews, etc.). This feature will be critical for the XSS demonstration.
Your application should also have a display feature where the stored data is presented to users.
Use SQLite as the database backend.
Example: For an online store, users can edit their profiles, add product descriptions, or leave reviews. These descriptions or reviews are then visible to other users who visit the product page.

Introduce an XSS Vulnerability:

Intentionally introduce an XSS vulnerability related to your application's user input data feature.
Document where you introduced the vulnerability and why it's an issue.
Demonstration:

Show how an attacker might exploit the XSS vulnerability you introduced.
Demonstrate the attack's impact (e.g., stealing a session cookie, displaying a fake login form, defacing the website, etc.).
Mitigation:

Explain the methods to prevent XSS vulnerabilities.
Modify your application to fix the vulnerability you introduced.
Demonstrate that your mitigation strategies are effective.

### Docker: 
run the following in git bash: 
cd Cross-Site-Scripting
docker build -t xss .
docker run -d -p 5000:5000 xss
