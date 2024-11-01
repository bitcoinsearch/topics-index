import os

import requests
import json
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class TopicsIndex:
    def get_ops_topics(self):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}

            url = "https://bitcoinops.org/topics.json"

            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an HTTPError if the response status is 4xx or 5xx

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()

                # Filter only the required fields (title, tags, and links)
                transformed_data = [
                    {
                        "title": item.get("title"),
                        "categories": item.get("categories"),
                        "link": item.get("optech_url"),
                        "synonyms": item.get("aliases")
                    }
                    for item in data
                ]
                self.save_topics_to_json(transformed_data)
            else:
                print(f"Failed to retrieve data. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download the repo: {e}")
        except json.JSONDecodeError:
            print("Failed to parse JSON response.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def save_topics_to_json(transformed_data: []):
        # Check if the file already exists
        if os.path.exists("topics.json"):
            # Check if the file is empty
            if os.path.getsize("topics.json") > 0:
                # Load existing data if file is non-empty
                with open("topics.json", "r") as file:
                    existing_data = json.load(file)
            else:
                # Initialize empty list if the file is empty
                existing_data = []
        else:
            existing_data = []

        # Create a set of existing titles for quick duplicate check
        existing_titles = {item["title"] for item in existing_data}

        # Filter out items that already exist in topics.json based on title
        new_data = [item for item in transformed_data if item["title"] not in existing_titles]

        # Append the new data to existing data
        existing_data.extend(new_data)

        # Save the updated data back to topics.json
        with open("topics.json", "w") as file:
            json.dump(existing_data, file, indent=4)

        print("New data has been added to 'topics.json'")



