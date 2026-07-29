# ⚙️ Configuration Guide

Welcome to the heart of the EL-STRIX customization! The entire appearance and content of your GitHub banners and stats are controlled by a single, easy-to-read file: `config/profile.json`.

Think of this file as the control panel for your GitHub profile. By simply updating the text here, the engine will automatically generate beautiful new graphics for you on its next run.

## 📝 The `profile.json` Structure

Here is a breakdown of what each field does and how you can personalize it.

### Personal Details
These fields drive the main text on your profile banners and terminal headers.
- **`username`**: Your GitHub handle (e.g., `"EL-STRIX"`).
- **`name`**: Your full name or alias.
- **`terminal_header`**: The text that appears at the top of your terminal-style banners (e.g., `"sujay@EL-STRIX"`).
- **`bio`**: A short, punchy description of what you do.
- **`location`**: Where you're based in the world.
- **`company`**: Where you currently work (leave empty `""` if not applicable).
- **`website`**: A link to your personal site or main project.
- **`email`**: Your professional contact email.
- **`linkedin`**: Your LinkedIn username or display name.
- **`portfolio`**: Link to your portfolio (or `"Coming Soon"`!).

### 💻 Tech Stack
This array allows you to categorize and list the technologies you work with. It's rendered into the beautiful tech cards on your profile.
```json
"tech_stack": [
  {
    "name": "Programming",
    "value": "C, C++, Java, Python, JS"
  }
]
```
Feel free to add as many categories as you like. We recommend keeping the `value` list concise so it looks great on the generated SVGs!

### 🚀 Featured Projects
Showcase what you're actively working on.
```json
"featured_projects": [
  {
    "name": "Finzo Banking System",
    "status": "Development Phase"
  }
]
```
The `status` helps visitors know if a project is completed, in planning, or actively being built.

---

### 💡 Pro Tips
- **Be careful with JSON syntax**: Make sure you don't miss any commas or quotes! If the JSON is invalid, the engine won't be able to run.
- **Keep it updated**: As you learn new skills or start new projects, just update this file, push to `main`, and let the GitHub Actions do the rest!
