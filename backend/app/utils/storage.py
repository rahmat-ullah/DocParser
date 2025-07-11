import os


def get_markdown_path(document_id, original_name):
    """
    Construct a file path for storing a markdown document.

    :param document_id: Unique identifier for the document.
    :param original_name: Original file name.
    :return: Constructed file path.
    """
    safe_name = original_name.replace(' ', '_')  # Replace spaces with underscores
    filename = f"{document_id}_{safe_name}.md"
    directory = "markdown_storage"  # Example directory name
    return os.path.join(directory, filename)


def save_markdown(content, path):
    """
    Save markdown content to a specified path.

    :param content: Markdown content to be saved.
    :param path: Path where the content should be saved.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)  # Ensure the directory exists
    with open(path, 'w') as file:
        file.write(content)


def delete_markdown(document):
    """
    Delete a markdown document file.

    :param document: Document to be deleted.
    """
    try:
        os.remove(document)
    except OSError as e:
        print(f"Error deleting {document}: {e}")

