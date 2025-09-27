
# build.py
#
# To run this script, use: pixi run build
#
import yaml
from pathlib import Path
import random
from jinja2 import Environment, FileSystemLoader

def generate_project_html(projects):
    # This function could be moved into Jinja macros in the future,
    # but for now we keep it here for simplicity.
    html = ""
    for project in projects:
        links_html = ""
        for link in project.get("links", []):
            if link.get("enabled"):
                links_html += f'<a href="{link["url"]}" target="_blank" rel="noopener noreferrer" class="inline-block bg-gray-700 hover:bg-purple-500 text-teal-300 font-semibold py-2 px-4 rounded-lg transition-transform transform hover:scale-105">{link["text"]}</a>'
            else:
                links_html += f'<span class="inline-block bg-gray-800 text-gray-500 font-semibold py-2 px-4 rounded-lg cursor-not-allowed">{link["disabled_text"]}</span>'

        description_html = ""
        if "description" in project:
            description_html = f'<pre class="text-gray-300 mt-4 font-sans whitespace-pre-wrap">{project["description"]}</pre>'

        html += f"""
        <div class="bg-gray-800/50 backdrop-blur-sm border border-teal-400/20 rounded-xl p-6 transform -rotate-1 hover:rotate-0 hover:scale-105 transition-transform duration-300 ease-in-out shadow-lg shadow-teal-500/10">
            <h3 class="text-2xl font-bold text-teal-300">{project["name"]}</h3>
            <p class="text-purple-400 font-mono text-sm my-2">{project["collab"]}</p>
            {description_html}
            <div class="flex flex-wrap gap-4 mt-4">
                {links_html}
            </div>
        </div>
        """
    return html

def generate_equipment_html(equipments):
    html = ""
    for i, item in enumerate(equipments):
        award_html = ""
        if "award" in item:
            award_html = f'<p class="text-sm text-yellow-400 font-mono mt-2 animate-pulse">🏅 {item["award"]}</p>'
        
        specs_html = "<ul class='list-disc list-inside text-gray-300 space-y-1 mt-2'>"
        if isinstance(item["specs"], list):
            for spec in item["specs"]:
                specs_html += f"<li>{spec}</li>"
        else:
            specs_html += f"<li>{item['specs']}</li>"
        specs_html += "</ul>"

        rotation = "rotate-1" if i % 2 == 0 else "-rotate-1"

        html += f"""
        <div x-data=\"{{ open: false }}\" class=\"bg-gray-800/50 backdrop-blur-sm border border-purple-400/20 rounded-xl p-6 transform {rotation} hover:rotate-0 hover:scale-105 transition-transform duration-300 ease-in-out shadow-lg shadow-purple-500/10 cursor-pointer\" @mouseenter=\"open = true\" @mouseleave=\"open = false\" @click=\"open = !open\">
            <h3 class=\"text-xl font-bold text-purple-300\">{item["name"]}</h3>
            <div x-show=\"open\" x-transition class=\"mt-2\">
                {specs_html}
                {award_html}
            </div>
        </div>
        """
    return html

def generate_friends_html(friends):
    html = ""
    for i, friend in enumerate(friends):
        col_span = random.choice(["col-span-1", "col-span-2"])
        row_span = random.choice(["row-span-1"])
        img_height = random.choice(["h-40", "h-56", "h-64"])

        card_content = f"""
        <div class="{row_span} {col_span} bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-4 flex flex-col text-center transform hover:scale-105 transition-transform duration-300 ease-in-out overflow-hidden">
            <img src="{friend['photo_url']}" alt="{friend['name']}" class="w-full {img_height} object-cover rounded-md mb-4">
            <h3 class="text-xl font-bold text-white">{friend['name']}</h3>
            <p class="text-sm text-teal-400 font-mono">{friend['affiliation']['type']}: {friend['affiliation']['name']}</p>
            <p class="text-gray-400 mt-2 text-sm flex-grow">{friend['description']}</p>
        </div>
        """

        if friend.get("url") and friend["url"] != "#":
            html += f'<a href="{friend["url"]}" target="_blank" rel="noopener noreferrer" class="block">{card_content}</a>'
        else:
            html += card_content
            
    return html

def main():
    CWD = Path(__file__).parent
    
    Path(CWD / "out").mkdir(exist_ok=True)

    # --- Data Loading ---
    with open(CWD / "config.yaml", "r") as f:
        config_data = yaml.safe_load(f)
    with open(CWD / "projects.yaml", "r") as f:
        projects_data = yaml.safe_load(f)
    with open(CWD / "equipment.yaml", "r") as f:
        equipment_data = yaml.safe_load(f)
    with open(CWD / "friends.yaml", "r") as f:
        friends_data = yaml.safe_load(f)
    
    random.shuffle(friends_data)

    # --- HTML Generation (could be moved to Jinja in the future) ---
    projects_html = generate_project_html(projects_data)
    equipment_html = generate_equipment_html(equipment_data)
    friends_html = generate_friends_html(friends_data)

    # --- Jinja2 Templating ---
    env = Environment(loader=FileSystemLoader(CWD / 'templates'))
    template = env.get_template('index.html')

    # Combine all data into a single context for Jinja
    context = {
        "projects": projects_html,
        "equipment": equipment_html,
        "friends": friends_html,
        **config_data
    }

    output_html = template.render(context)

    # Write the final HTML file
    output_path = CWD / "out" / "index.html"
    with open(output_path, "w") as f:
        f.write(output_html)
        
    print(f"✅ Website built successfully! Output at {output_path}")

if __name__ == "__main__":
    main()
