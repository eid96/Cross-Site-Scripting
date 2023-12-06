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

###Docker
* docker build -t xss .
* docker run -d -p 5000:5000 xss
* docker run xss 

##Description Assignment 3 
## (20) **Database Integration:**

- Integrate a lightweight database, e.g., JSON-based storage or SQLite, to persistently save user data.
- Design efficient database schemas that optimize retrieval and storage operations while ensuring data security.

## (20) Basic **User Authentication:**

<aside>
💡 Remember to document security challenges and mitigations

</aside>

- Set up a standard authentication system that allows users to sign up using a username and password.
- Store user credentials securely in the database, leveraging advanced hashing and salting techniques, preferably with libraries like `bcrypt` or `hashlib`.

## (20) **Protection Against Brute Force Attacks:**

<aside>
💡 Remember to document security challenges and mitigations

</aside>

- Embed a robust rate-limiting mechanism in the system to discourage repetitive password guess attempts.
- Impose a mandatory time-out after three consecutive failed login attempts.

*Note: You can test this by attempting to access an API endpoint several times without the correct authentication token, or trying to log in with incorrect credentials*

## (20) **Two-Factor Authentication (2FA):**

<aside>
💡 Remember to document security challenges and mitigations

</aside>

- Incorporate a time-based one-time password (TOTP) system for an enhanced security layer following either the OAuth2 or conventional login. Utilize the `pyotp` library.
- Upon registration, generate and display a QR code for users, allowing integration with 2FA apps like Google Authenticator.
- During the login phase, request that the user input the TOTP from their authenticator app.

## (20) Understanding the Concepts of **OAuth2:**

<aside>
💡 Remember to document security challenges and mitigations. Also here, you can document the benefits of OAuth

</aside>

- Develop an OAuth2 client using the Authorization Code Flow.
- Enable users to register or log in via established third-party providers (e.g., Google, GitHub).
- Fetch and securely store user details from the third-party provider in the database.
## **Documentation Requirement:**

For each task, detail:

- **Security Challenges:** Identify challenges related to the specific feature.
- **Vulnerabilities & Mitigations:** List potential vulnerabilities and ways to counteract them.

---

## **Deliverables:**

1. **Repository or Folder:** This should contain code, database schemas, templates, and other vital files.
2. **Report:** Includes:
    - **Architectural Choices:** Why they were made.
    - **Resources:** Libraries, tools, or external resources used and why.
    - **Challenges & Solutions:** Difficulties encountered and how they were resolved.
    - **Recommendations:** Suggestions for further system improvements.

---

## **Evaluation Criteria:**

1. **Functionality:** How well the system operates and follows specifications.
2. **Security Excellence:** Adherence to top security practices from the course.
3. **Code Quality:** Organization, readability, and documentation of the code.
4. **Innovative Features:** Additional features enhancing user experience or security.
5. **Documentation Depth:** Clarity and thoroughness in the report and code comments.


### Changes for task 3: 
* All of userfunctionality related to the table is moved to static/user_functions.py
* All blog post related are moved to posts.py 
* HTML related coode still found in "templates#/.." 
* simple routing still found in app.py

### Client secret and id 
* client secret and ID can be found in project report in section 4.5 and needs to be copied in to app.py for the code to run
* CLIENT_ID = "insert ID from pdf"
* CLIENT_SECRET = "insert secret from pdf"
