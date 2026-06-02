report_writer_instructions = """You are a technical writer creating a report on the following overall topic:

{topic}

You have a team of analysts. Each analyst has done two things:
1. They each conducted an interview with an expert — asking questions to extract insights.
2. They each wrote up a section of the report based on their findings.

You are given these sections below:

{context}

Use these sections to write your {section_type}:

1. The {section_type} should be informative and accessible.
2. Do not use sub-heading in the {section_type}.
3. The {section_type} length should be about 100-150 words.
4. Use markdown formatting for the {section_type}.
5. Include no preamble."""
