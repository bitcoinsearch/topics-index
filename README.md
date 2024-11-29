# Bitcoin Topics Index

An extensive index of Bitcoin-related topics, combining and enhancing the established [Bitcoin Optech Topics](https://bitcoinops.org/en/topics/) with additional relevant entries.

See [TOPICS.md](TOPICS.md) for the categorized index or [topics.json](topics.json) for the machine-readable format.

## Repository Structure

```
.
├── topics/             # Bitcoin topics
│   ├── topic1.yaml
│   ├── topic2.yaml
│   └── ...
├── scripts/           # Build and maintenance scripts
│   └── build_index.py
├── topics.json       # Machine-readable index
├── TOPICS.md         # Generated documentation
└── README.md
```

## Topics Format

Each topic is defined in YAML format with the following structure:

```yaml
title: "Topic Title" # Display name of the topic
slug: "topic-slug" # URL-friendly identifier
categories: # List of categories this topic belongs to
  - "Category 1"
  - "Category 2"
aliases: # Optional: Alternative names for the topic
  - "Alternative Name"
  - "Another Name"
excerpt: "A comprehensive description of the topic."
```

## Category Topics

Each category automatically includes a miscellaneous topic that covers content which doesn't fit neatly into other specific topics.
By default, these topics use slugs generated from the category name (lowercase with hyphens).

For categories that need custom slugs, define them in [category-slugs.yaml](category-slugs.yaml).

## Usage

### Building the Index

To build the combined index and documentation:

```bash
python scripts/build_index.py
```

This will:

1. Fetch the latest topics from Bitcoin Optech's [/topics.json](https://bitcoinops.org/topics.json).
2. Combine them with additional topics from the `topics/` directory
3. Generate misc topics for each category using slugs from `category-slugs.yaml` where defined
4. Generate `topics.json` with the complete topics data
5. Create `TOPICS.md` with categorized listings

### Adding Topics

1. Create a new YAML file in the `topics/` directory
2. Follow the topics format described above
3. Run the build script to update the index
