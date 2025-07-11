import re
from typing import List, Optional
from ..parsers.ast_models import TableBlock

def parse_markdown_table_to_table_block(markdown_table: str, caption: Optional[str] = None) -> Optional[TableBlock]:
    """
    Parses a Markdown table string into a TableBlock object.

    Args:
        markdown_table: The Markdown table as a string.
        caption: Optional caption for the table.

    Returns:
        A TableBlock object if parsing is successful, otherwise None.
    """
    if not markdown_table or not isinstance(markdown_table, str):
        return None

    lines = [line.strip() for line in markdown_table.strip().split('\n')]

    # Filter out empty lines
    lines = [line for line in lines if line]

    if len(lines) < 2:  # Need at least header and separator
        return None

    # Helper to split a Markdown table row
    def split_row(row_str: str) -> List[str]:
        if not row_str.startswith('|') or not row_str.endswith('|'):
            # Non-standard markdown table row, try splitting by |
            # This is a fallback, proper markdown tables should have leading/trailing pipes
            cells = [cell.strip() for cell in row_str.split('|')]
            # If the split results in empty strings at start/end due to no leading/trailing pipes
            if not cells[0]: cells.pop(0)
            if not cells[-1]: cells.pop(-1)
            return cells
        return [cell.strip() for cell in row_str[1:-1].split('|')]

    headers = split_row(lines[0])

    # Validate separator line
    separator_line = lines[1]
    if not all(re.match(r"^-+$", cell.strip()) for cell in split_row(separator_line)):
         # Try to match variants like :---: or ---
        if not all(re.match(r"^:?-+:?$", cell.strip()) for cell in split_row(separator_line)):
            # If separator is not valid, this might not be a table or a poorly formatted one
            return None

    rows_data: List[List[str]] = []
    for i in range(2, len(lines)):
        row_cells = split_row(lines[i])
        # Ensure row cells match header count, pad if necessary (though LLM should be good)
        if len(row_cells) < len(headers):
            row_cells.extend([""] * (len(headers) - len(row_cells)))
        elif len(row_cells) > len(headers):
            row_cells = row_cells[:len(headers)]
        rows_data.append(row_cells)

    if not headers or not rows_data: # if only headers and separator but no data rows
        return None

    return TableBlock(headers=headers, rows=rows_data, caption=caption)

if __name__ == '__main__':
    # Test cases
    md_table_1 = """
    | Header 1 | Header 2 | Header 3 |
    |----------|----------|----------|
    | R1C1     | R1C2     | R1C3     |
    | R2C1     | R2C2     | R2C3     |
    """
    table_block_1 = parse_markdown_table_to_table_block(md_table_1, "Test Table 1")
    if table_block_1:
        print("Table 1 Parsed:")
        print(f"  Headers: {table_block_1.headers}")
        print(f"  Rows: {table_block_1.rows}")
        print(f"  Caption: {table_block_1.caption}")
    else:
        print("Table 1 Parsing Failed.")

    md_table_2 = """
    | Fruit    | Color  |
    | :------- | :----- |
    | Apple    | Red    |
    | Banana   | Yellow |
    | Grapes   | Purple |
    """
    table_block_2 = parse_markdown_table_to_table_block(md_table_2)
    if table_block_2:
        print("\nTable 2 Parsed:")
        print(f"  Headers: {table_block_2.headers}")
        print(f"  Rows: {table_block_2.rows}")
    else:
        print("Table 2 Parsing Failed.")

    md_table_no_data = """
    | Header 1 | Header 2 |
    |----------|----------|
    """
    table_block_no_data = parse_markdown_table_to_table_block(md_table_no_data)
    if table_block_no_data:
         print("\nTable No Data Parsed (should not happen):")
    else:
        print("\nTable No Data Parsing Failed (expected).")

    md_invalid_table = "This is not a table."
    table_block_invalid = parse_markdown_table_to_table_block(md_invalid_table)
    if table_block_invalid:
        print("\nInvalid Table Parsed (should not happen).")
    else:
        print("\nInvalid Table Parsing Failed (expected).")

    md_table_no_pipes = """
    Header 1 | Header 2 | Header 3
    ----------|----------|----------
    R1C1     | R1C2     | R1C3
    R2C1     | R2C2     | R2C3
    """
    # This case is currently not well supported by the strict check for leading/trailing pipes
    # but the fallback split might handle it.
    table_block_no_pipes = parse_markdown_table_to_table_block(md_table_no_pipes, "No Pipes Table")
    if table_block_no_pipes:
        print("\nNo Pipes Table Parsed:")
        print(f"  Headers: {table_block_no_pipes.headers}")
        print(f"  Rows: {table_block_no_pipes.rows}")
    else:
        print("\nNo Pipes Table Parsing Failed.")

    md_table_with_empty_cells = """
    | Name  | Age | City      |
    |-------|-----|-----------|
    | Alice | 30  | New York  |
    | Bob   |     | San Fran  |
    | Eve   | 25  |           |
    """
    table_block_empty_cells = parse_markdown_table_to_table_block(md_table_with_empty_cells)
    if table_block_empty_cells:
        print("\nTable with Empty Cells Parsed:")
        print(f"  Headers: {table_block_empty_cells.headers}")
        print(f"  Rows: {table_block_empty_cells.rows}")
    else:
        print("\nTable with Empty Cells Parsing Failed.")
