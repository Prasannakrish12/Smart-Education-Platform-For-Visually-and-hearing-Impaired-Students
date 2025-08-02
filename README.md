# Smart Education Platform for Visually and Hearing Impaired Students

An inclusive educational web platform built using Python and Flask that offers customized learning experiences for students with visual and hearing impairments. The platform adapts its content and structure to cater to different accessibility needs, including screen reader support, sign language interpretation, and optimized navigation.

## 🔧 Project Structure

Smart edu/
│
├── pycache/
│   ├── hearing.cpython-<…>.pyc
│   └── visually.cpython-<…>.pyc
│
├── templates/
│   ├── about.html
│   ├── accessibility.html
│   ├── contact.html
│   ├── courses.html
│   ├── hearing.html
│   ├── index.html
│   ├── profile.html
│   └── visual.html
│
├── app.py                   # Flask application entry point
├── main.py                  # Backend controller logic
├── hearing.py               # Logic for hearing-impaired user interaction
├── visually.py              # Logic for visually-impaired user interaction
│
├── hearing.json             # JSON data for hearing-impaired content
├── visual.json              # JSON data for visually-impaired content
│
└── README.md                # Project documentation


## 🌟 Features

- Separate user flows for:
  - 👁️ Visually Impaired Users
  - 👂 Hearing Impaired Users
- Custom HTML templates for accessibility
- Flask backend routing for page logic
- JSON-based content loading for modularity
- Clean UI built with semantic HTML for screen reader compatibility


## 🚀 How to Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Prasannakrish12/Smart-Education-Platform-For-Visually-and-hearing-Impaired-Students
   cd Smart-Education-Platform-For-Visually-and-hearing-Impaired-Students

	2.	Install Dependencies

pip install flask


	3.	Run the Application

python app.py


	4.	Open your browser and go to http://127.0.0.1:5000


📄 File Descriptions
	•	app.py – Starts the Flask server and loads routes.
	•	main.py – Handles backend logic and page redirection.
	•	visually.py – Contains features and functions tailored for visually impaired users.
	•	hearing.py – Contains features and functions tailored for hearing impaired users.
	•	visual.json / hearing.json – Store accessibility-specific content dynamically.
	•	templates/ – All user interface HTML files.


🔍 Accessibility Focus

This project follows accessibility-first principles:
	•	Semantic HTML for screen reader compatibility
	•	Simple navigation structure
	•	Color contrast and large font for visibility
	•	Dedicated pages for screen readers or sign-language content


💡 Future Enhancements
	•	Text-to-speech integration for visually impaired users
	•	Sign language video support
	•	User registration & personalization
	•	Admin dashboard for content management


📬 Contact

For queries or contributions:

Prasanna S
📧 Email: [prasannas4463@gmail.com](mailto:prasannas4463@gmail.com)  
🐙 GitHub: [Prasannakrish12](https://github.com/Prasannakrish12)

## 📄 License

This project is licensed under the [Creative Commons BY-NC-ND 4.0 License](https://creativecommons.org/licenses/by-nc-nd/4.0/).

🚫 No commercial use  
🚫 No modifications  
✅ Free to share with credit

Copyright © 2025 Prasanna S. All rights reserved.