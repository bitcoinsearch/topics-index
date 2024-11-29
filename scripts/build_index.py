import requests
import json
import yaml
import os
import logging
from typing import Dict, List
from collections import defaultdict
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TopicsBuilder:
    def __init__(self, optech_topics_url: str, topics_dir: str, root_dir: str):
        self.optech_topics_url = optech_topics_url
        self.topics_dir = topics_dir
        self.root_dir = root_dir
        self.category_slugs = self.load_category_slugs()

    def load_category_slugs(self) -> Dict[str, str]:
        """Load category slug mappings from category-slugs.yaml."""
        slugs_path = os.path.join(self.root_dir, "category-slugs.yaml")
        if os.path.exists(slugs_path):
            with open(slugs_path, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    def fetch_optech_topics(self) -> List[Dict]:
        """Fetch topics directly from the Bitcoin Optech website."""
        response = requests.get(self.optech_topics_url)
        response.raise_for_status()
        return response.json()

    def load_yaml_file(self, filepath: str) -> Dict:
        """Load a single YAML file."""
        with open(filepath, "r") as f:
            return yaml.safe_load(f)

    def load_topics(self) -> List[Dict]:
        """Load all YAML files from the topics directory."""
        topics = []
        if os.path.exists(self.topics_dir):
            for filename in os.listdir(self.topics_dir):
                if filename.endswith(".yaml"):
                    filepath = os.path.join(self.topics_dir, filename)
                    topic = self.load_yaml_file(filepath)
                    topics.append(topic)
        return topics

    def get_all_categories(self, topics: List[Dict]) -> set:
        """Extract all unique categories from the topics."""
        categories = set()
        for topic in topics:
            topic_categories = topic.get("categories", [])
            if isinstance(topic_categories, str):
                topic_categories = [topic_categories]
            categories.update(topic_categories)
        return categories

    def get_category_slug(self, category: str) -> str:
        """Get the slug for a category, using custom mapping if available."""
        return self.category_slugs.get(category, category.lower().replace(" ", "-"))

    def generate_misc_topics(self, categories: set) -> List[Dict]:
        """Generate miscellaneous topics for each category."""
        misc_topics = []
        for category in categories:
            # Use custom slug if defined, otherwise use default slug format
            slug = self.get_category_slug(category)

            # Create misc topic for the category
            misc_topic = {
                "title": f"{category} (Miscellaneous)",
                "slug": slug,
                "categories": [category],
                "excerpt": f"A catch-all for information related to {category}, covering content that doesn't fit neatly into specific topics.",
            }

            misc_topics.append(misc_topic)

        logger.info(
            f"Generated miscellaneous topic for categories: {', '.join(categories)}"
        )
        return misc_topics

    def build_topics(self) -> List[Dict]:
        """Build complete topics list by combining Optech and additional topics."""
        optech_topics = self.fetch_optech_topics()
        additional_topics = self.load_topics()

        # Get all unique categories
        all_categories = self.get_all_categories(optech_topics + additional_topics)

        # Generate miscellaneous topics
        misc_topics = self.generate_misc_topics(all_categories)

        # Create a dictionary of topics by slug for easy lookup
        topic_dict = {topic["slug"]: topic for topic in optech_topics}

        # Add or override with additional topics and misc topics
        for topic in additional_topics + misc_topics:
            topic_dict[topic["slug"]] = topic

        # Convert back to list and sort by title
        combined_topics = list(topic_dict.values())
        combined_topics.sort(key=lambda x: x["title"].lower())

        return combined_topics

    def write_topics_index(self, topics: List[Dict]):
        """Write the topics index to a JSON file in the root directory."""
        output_path = os.path.join(self.root_dir, "topics.json")
        with open(output_path, "w") as f:
            json.dump(topics, f, indent=2, ensure_ascii=False)
        logger.info(f"Created topics index with {len(topics)} topics")

    def generate_topics_md(self, topics: List[Dict]):
        """Generate TOPICS.md documentation file in the root directory."""
        # Group topics by category
        categories_dict = defaultdict(list)
        unique_topics = set()

        for topic in topics:
            topic_categories = topic.get("categories", [])
            if isinstance(topic_categories, str):
                topic_categories = [topic_categories]

            # Add topic to each of its categories
            for category in topic_categories:
                # Create topic entry with aliases if they exist
                topic_entry = topic["title"]
                if "aliases" in topic and topic["aliases"]:
                    aliases_str = ", ".join(topic["aliases"])
                    topic_entry += f" (also covering: {aliases_str})"

                categories_dict[category].append(topic_entry)
                unique_topics.add(topic["title"])

        # Sort categories and their topics
        categories = sorted(categories_dict.keys())
        for category in categories:
            categories_dict[category].sort()

        # Generate markdown content
        content = []

        # Add summary line and miscellaneous topics note
        content.append(
            f"*{len(categories)} categories for {len(unique_topics)} unique topics, with many appearing in multiple categories.*\n"
        )
        content.append(
            "*Note: Each category includes a miscellaneous topic to support content that doesn't fit neatly into specific topics.*\n"
        )

        # Add table of contents as a single line
        toc_items = []
        for category in categories:
            anchor = category.lower().replace(" ", "-")
            toc_items.append(f"[{category}](#{anchor})")
        content.append(" | ".join(toc_items))
        content.append("")  # Empty line after ToC

        # Add categories and their topics
        for category in categories:
            content.append(f"## {category}")
            for topic in categories_dict[category]:
                content.append(f"- {topic}")
            content.append("")  # Empty line between categories

        # Write to file in root directory
        output_path = os.path.join(self.root_dir, "TOPICS.md")
        with open(output_path, "w") as f:
            f.write("\n".join(content))
        logger.info("Created TOPICS.md documentation")

    def build(self):
        """Main function to build topics."""
        try:
            topics = self.build_topics()
            self.write_topics_index(topics)
            self.generate_topics_md(topics)
        except Exception as e:
            logger.error(f"Error during topics building: {str(e)}")
            raise


def main():
    # Get the absolute path to the repository root (assuming script is in scripts/)
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent

    optech_topics_url = "https://bitcoinops.org/topics.json"
    topics_dir = os.path.join(root_dir, "topics")

    builder = TopicsBuilder(
        optech_topics_url=optech_topics_url,
        topics_dir=topics_dir,
        root_dir=str(root_dir),
    )
    builder.build()


if __name__ == "__main__":
    main()
