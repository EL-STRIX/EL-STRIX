<div align="center">

# {{ name }}

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/svg/dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/svg/light.svg" />
  <img alt="EL-STRIX Profile Banner" src="assets/svg/dark.svg" width="100%" />
</picture>

> {{ bio }}

---

</div>

## 📊 GitHub Stats

| Metric | Value |
|--------|-------|
| ⭐ Total Stars | **{{ total_stars }}** |
| 🍴 Total Forks | **{{ total_forks }}** |
| 📦 Public Repos | **{{ public_repos }}** |
| 👥 Followers | **{{ followers }}** |
| 👤 Following | **{{ following }}** |

{% if featured_repos %}
## 🚀 Featured Projects

{% for repo in featured_repos %}
### [{{ repo.name }}]({{ repo.url }})
> {{ repo.description }}
> `{{ repo.language }}` • ⭐ {{ repo.stars }}

{% endfor %}
{% endif %}

{% if languages %}
## 🛠️ Languages

{% for lang, pct in languages.items() %}
- **{{ lang }}**: {{ pct }}%
{% endfor %}
{% endif %}

---

{% include "footer.md" %}
